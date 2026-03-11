terraform {
  required_version = "1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.22.0"
    }
  }
}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

data "aws_iam_policy_document" "key_policy" {
  statement {
    actions   = ["kms:*"]
    effect    = "Allow"
    resources = ["*"]
    sid       = "EnableIAMUserPermissions"

    principals {
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
      type        = "AWS"
    }
  }

  statement {
    actions = [
      "kms:Decrypt",
      "kms:Describe*",
      "kms:Encrypt",
      "kms:GenerateDataKey*",
      "kms:ReEncrypt*",
    ]
    effect    = "Allow"
    resources = ["*"]
    sid       = "AllowCloudWatchLogs"

    condition {
      test     = "ArnLike"
      values   = ["arn:aws:logs:${data.aws_region.current.id}:${data.aws_caller_identity.current.account_id}:log-group:*"]
      variable = "kms:EncryptionContext:aws:logs:arn"
    }

    principals {
      identifiers = ["logs.${data.aws_region.current.id}.amazonaws.com"]
      type        = "Service"
    }
  }

  dynamic "statement" {
    for_each = length(var.kms_allowed_principal_arns) > 0 ? [1] : []
    content {
      actions = [
        "kms:Decrypt",
        "kms:GenerateDataKey*",
      ]
      effect    = "Allow"
      resources = ["*"]
      sid       = "AllowAdditionalPrincipals"

      condition {
        test     = "StringEquals"
        variable = "kms:ViaService"
        values   = ["s3.${data.aws_region.current.region}.amazonaws.com"]
      }

      principals {
        identifiers = var.kms_allowed_principal_arns
        type        = "AWS"
      }
    }
  }
}

resource "aws_kms_key" "main" {
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  deletion_window_in_days  = var.deletion_window_in_days
  description              = "KMS key for encrypting ${var.project_name}-${var.environment} resources"
  enable_key_rotation      = true
  key_usage                = "ENCRYPT_DECRYPT"
  multi_region             = false
  policy                   = data.aws_iam_policy_document.key_policy.json
  rotation_period_in_days  = var.rotation_period_in_days
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-kms"
  })
}

resource "aws_kms_alias" "main" {
  name          = var.alias_name
  target_key_id = aws_kms_key.main.key_id
}
