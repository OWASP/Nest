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

resource "aws_s3_bucket" "zappa" { # NOSONAR
  bucket        = var.zappa_s3_bucket
  force_destroy = var.force_destroy_bucket
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-zappa-deployments"
  })
}

resource "aws_s3_bucket_public_access_block" "zappa" {
  block_public_acls       = true
  block_public_policy     = true
  bucket                  = aws_s3_bucket.zappa.id
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "zappa" {
  bucket = aws_s3_bucket.zappa.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "zappa" {
  bucket = aws_s3_bucket.zappa.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "zappa" {
  bucket = aws_s3_bucket.zappa.id

  rule {
    abort_incomplete_multipart_upload {
      days_after_initiation = var.abort_incomplete_multipart_upload_days
    }
    id = "delete-old-versions"
    noncurrent_version_expiration {
      noncurrent_days = var.noncurrent_version_expiration_days
    }
    status = "Enabled"
  }
}

data "aws_iam_policy_document" "zappa" {
  statement {
    actions = ["s3:*"]
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
    effect = "Deny"
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    resources = [
      aws_s3_bucket.zappa.arn,
      "${aws_s3_bucket.zappa.arn}/*",
    ]
    sid = "EnforceTls"
  }
}

resource "aws_s3_bucket_policy" "zappa" {
  bucket = aws_s3_bucket.zappa.id
  policy = data.aws_iam_policy_document.zappa.json
}
