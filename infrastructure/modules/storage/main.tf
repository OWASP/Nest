terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

# S3 Bucket for Zappa Deployments
resource "aws_s3_bucket" "zappa" {
  bucket = var.zappa_s3_bucket

  tags = {
    Name = "${var.project_name}-${var.environment}-zappa-deployments"
  }
  force_destroy = true
}

# S3 Bucket for Zappa Logs
resource "aws_s3_bucket" "zappa_logs" {
  bucket = "${var.zappa_s3_bucket}-logs"

  tags = {
    Name = "${var.project_name}-${var.environment}-zappa-deployments-logs"
  }
}

resource "aws_s3_bucket_ownership_controls" "zappa_logs" {
  bucket = aws_s3_bucket.zappa_logs.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

# Grant log-delivery-write ACL to the new bucket
resource "aws_s3_bucket_acl" "zappa_logs" {
  depends_on = [aws_s3_bucket_ownership_controls.zappa_logs]
  bucket     = aws_s3_bucket.zappa_logs.id
  acl        = "log-delivery-write"
}

# Enable logging for the zappa bucket
resource "aws_s3_bucket_logging" "zappa" {
  bucket = aws_s3_bucket.zappa.id

  target_bucket = aws_s3_bucket.zappa_logs.id
  target_prefix = "log/"
}

# Block public access
resource "aws_s3_bucket_public_access_block" "zappa" {
  bucket = aws_s3_bucket.zappa.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable versioning
resource "aws_s3_bucket_versioning" "zappa" {
  bucket = aws_s3_bucket.zappa.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "zappa" {
  bucket = aws_s3_bucket.zappa.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Lifecycle rule to clean up old versions
resource "aws_s3_bucket_lifecycle_configuration" "zappa" {
  bucket = aws_s3_bucket.zappa.id

  rule {
    id     = "delete-old-versions"
    status = "Enabled"

    noncurrent_version_expiration {
      noncurrent_days = 30
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# Enforce HTTPS-only access
data "aws_iam_policy_document" "zappa" {
  statement {
    sid    = "EnforceTls"
    effect = "Deny"
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    actions = ["s3:*"]
    resources = [
      aws_s3_bucket.zappa.arn,
      "${aws_s3_bucket.zappa.arn}/*",
    ]
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}

resource "aws_s3_bucket_policy" "zappa" {
  bucket = aws_s3_bucket.zappa.id
  policy = data.aws_iam_policy_document.zappa.json
}
