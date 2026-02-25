terraform {
  required_version = "1.14.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.22.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.7.2"
    }
  }
}

locals {
  common_tags = {
    Environment = "state"
    ManagedBy   = "Terraform"
    Project     = var.project_name
  }
  state_environments = toset(var.state_environments)
}

module "kms" {
  source = "../modules/kms"

  common_tags  = local.common_tags
  environment  = "state"
  project_name = var.project_name
}

resource "random_id" "suffix" {
  byte_length = 4
}

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "logs" {
  for_each = local.state_environments

  statement {
    actions   = ["s3:PutObject"]
    effect    = "Allow"
    resources = ["${aws_s3_bucket.logs[each.key].arn}/*"]
    sid       = "s3-log-delivery"

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = [aws_s3_bucket.state[each.key].arn]
    }
    principals {
      identifiers = ["logging.s3.amazonaws.com"]
      type        = "Service"
    }
  }
}

data "aws_iam_policy_document" "state_https_only" {
  for_each  = local.state_environments
  policy_id = "ForceHTTPS"

  statement {
    actions = ["s3:*"]
    effect  = "Deny"
    sid     = "HTTPSOnly"

    resources = [
      aws_s3_bucket.state[each.key].arn,
      "${aws_s3_bucket.state[each.key].arn}/*",
    ]

    condition {
      test     = "Bool"
      values   = ["false"]
      variable = "aws:SecureTransport"
    }
    principals {
      identifiers = ["*"]
      type        = "AWS"
    }
  }
}

resource "aws_dynamodb_table" "state_lock" {
  for_each = local.state_environments

  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  name         = "${var.project_name}-${each.key}-terraform-state-lock"
  tags = merge(local.common_tags, {
    Environment = each.key
    Name        = "${var.project_name}-${each.key}-terraform-state-lock"
  })

  attribute {
    name = "LockID"
    type = "S"
  }
  lifecycle {
    prevent_destroy = true
  }
  point_in_time_recovery {
    enabled = true
  }
  server_side_encryption {
    enabled     = true
    kms_key_arn = module.kms.key_arn
  }
}

resource "aws_s3_bucket" "logs" { # NOSONAR
  for_each = local.state_environments

  bucket = "${var.project_name}-${each.key}-terraform-state-logs-${random_id.suffix.hex}"
  tags = merge(local.common_tags, {
    Environment = each.key
    Name        = "${var.project_name}-${each.key}-terraform-state-logs"
  })

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  for_each = local.state_environments

  bucket = aws_s3_bucket.logs[each.key].id

  rule {
    id     = "expire-logs"
    status = "Enabled"

    abort_incomplete_multipart_upload {
      days_after_initiation = var.abort_incomplete_multipart_upload_days
    }
    noncurrent_version_expiration {
      noncurrent_days = var.noncurrent_version_expiration_days
    }
    expiration {
      days = var.expire_log_days
    }
  }
}

resource "aws_s3_bucket_policy" "logs" {
  for_each = local.state_environments

  bucket = aws_s3_bucket.logs[each.key].id
  policy = data.aws_iam_policy_document.logs[each.key].json
}

resource "aws_s3_bucket_public_access_block" "logs" {
  for_each = local.state_environments

  block_public_acls       = true
  block_public_policy     = true
  bucket                  = aws_s3_bucket.logs[each.key].id
  ignore_public_acls      = true
  restrict_public_buckets = true
}

#trivy:ignore:AVD-AWS-0132
resource "aws_s3_bucket_server_side_encryption_configuration" "logs" {
  for_each = local.state_environments

  bucket = aws_s3_bucket.logs[each.key].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "logs" {
  for_each = local.state_environments

  bucket = aws_s3_bucket.logs[each.key].id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket" "state" { # NOSONAR
  for_each = local.state_environments

  bucket              = "${var.project_name}-${each.key}-terraform-state-${random_id.suffix.hex}"
  object_lock_enabled = true
  tags = merge(local.common_tags, {
    Environment = each.key
    Name        = "${var.project_name}-${each.key}-terraform-state"
  })

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "state" {
  for_each = local.state_environments

  bucket = aws_s3_bucket.state[each.key].id

  rule {
    id     = "delete-old-versions"
    status = "Enabled"

    abort_incomplete_multipart_upload {
      days_after_initiation = var.abort_incomplete_multipart_upload_days
    }
    noncurrent_version_expiration {
      noncurrent_days = var.noncurrent_version_expiration_days
    }
  }
}

resource "aws_s3_bucket_logging" "state" {
  for_each = local.state_environments

  bucket        = aws_s3_bucket.state[each.key].id
  target_bucket = aws_s3_bucket.logs[each.key].id
  target_prefix = "s3/"
}

resource "aws_s3_bucket_object_lock_configuration" "state" {
  for_each = local.state_environments

  bucket = aws_s3_bucket.state[each.key].id

  depends_on = [aws_s3_bucket_versioning.state[each.key]]

  rule {
    default_retention {
      days = 30
      mode = "GOVERNANCE"
    }
  }
}

resource "aws_s3_bucket_policy" "state" {
  for_each = local.state_environments

  bucket = aws_s3_bucket.state[each.key].id
  policy = data.aws_iam_policy_document.state_https_only[each.key].json
}

resource "aws_s3_bucket_public_access_block" "state" {
  for_each = local.state_environments

  block_public_acls       = true
  block_public_policy     = true
  bucket                  = aws_s3_bucket.state[each.key].id
  ignore_public_acls      = true
  restrict_public_buckets = true
}

#trivy:ignore:AVD-AWS-0132
resource "aws_s3_bucket_server_side_encryption_configuration" "state" {
  for_each = local.state_environments

  bucket = aws_s3_bucket.state[each.key].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "state" {
  for_each = local.state_environments

  bucket = aws_s3_bucket.state[each.key].id

  versioning_configuration {
    status = "Enabled"
  }
}
