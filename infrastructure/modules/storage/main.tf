# S3 Bucket for Zappa Deployments
resource "aws_s3_bucket" "zappa" {
  bucket = var.zappa_s3_bucket

  tags = {
    Name = "${var.project_name}-${var.environment}-zappa-deployments"
  }
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
