terraform {
  required_version = "1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.22.0"
    }
  }
}

locals {
  common_tags = {
    Environment = "bootstrap"
    ManagedBy   = "Terraform"
    Project     = var.project_name
  }
  environments = toset(var.environments)
}

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "terraform" {
  for_each = local.environments

  statement {
    actions = [
      "s3:GetObject",
      "s3:ListBucket",
      "s3:PutObject",
    ]
    effect = "Allow"
    resources = [
      "arn:aws:s3:::${var.project_name}-*",
      "arn:aws:s3:::${var.project_name}-*/*",
    ]
    sid = "S3StateAccess"
  }

  statement {
    actions = [
      "dynamodb:DeleteItem",
      "dynamodb:DescribeTable",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
    ]
    effect = "Allow"
    resources = [
      "arn:aws:dynamodb:*:${data.aws_caller_identity.current.account_id}:table/${var.project_name}-terraform-state-lock-${each.key}",
    ]
    sid = "DynamoDBStateLocking"
  }
}

resource "aws_iam_policy" "terraform" {
  for_each = local.environments

  name   = "${var.project_name}-${each.key}-terraform"
  policy = data.aws_iam_policy_document.terraform[each.key].json
  tags = merge(local.common_tags, {
    Environment = each.key
    Name        = "${var.project_name}-${each.key}-terraform"
  })
}

resource "aws_iam_role" "terraform" {
  for_each = local.environments

  name = "${var.project_name}-${each.key}-terraform"
  tags = merge(local.common_tags, {
    Environment = each.key
    Name        = "${var.project_name}-${each.key}-terraform"
  })

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Condition = {
          StringEquals = {
            "sts:ExternalId" = "${var.project_name}-${each.key}-terraform"
          }
        }
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/${var.project_name}-${each.key}"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "terraform" {
  for_each = local.environments

  policy_arn = aws_iam_policy.terraform[each.key].arn
  role       = aws_iam_role.terraform[each.key].name
}
