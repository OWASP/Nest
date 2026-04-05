terraform {
  required_version = "~> 1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.36.0"
    }
  }
}

resource "aws_s3_bucket" "nest_shared_data" { # NOSONAR
  bucket = var.bucket_name

  lifecycle {
    prevent_destroy = true
  }

  tags = merge(var.common_tags, {
    Name = var.bucket_name
  })
}

resource "aws_s3_bucket_public_access_block" "nest_shared_data" {
  bucket = aws_s3_bucket.nest_shared_data.id

  block_public_acls       = true
  block_public_policy     = false
  ignore_public_acls      = true
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "nest_shared_data" {
  bucket     = aws_s3_bucket.nest_shared_data.id
  depends_on = [aws_s3_bucket_public_access_block.nest_shared_data]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = ["s3:GetObject"]
        Effect    = "Allow"
        Principal = "*"
        Resource  = ["${aws_s3_bucket.nest_shared_data.arn}/${var.public_read_object_key}"]
        Sid       = "AllowPublicReadNestDump"
      },
      {
        Action = "s3:*"
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
        Effect = "Deny"
        Principal = {
          AWS = "*"
        }
        Resource = [
          aws_s3_bucket.nest_shared_data.arn,
          "${aws_s3_bucket.nest_shared_data.arn}/*"
        ]
        Sid = "HTTPSOnly"
      }
    ]
  })
}

resource "aws_s3_bucket_server_side_encryption_configuration" "nest_shared_data" {
  bucket = aws_s3_bucket.nest_shared_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "nest_shared_data" {
  bucket = aws_s3_bucket.nest_shared_data.id

  versioning_configuration {
    status = "Enabled"
  }
}
