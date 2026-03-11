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

resource "random_id" "suffix" {
  byte_length = 4
}

module "fixtures_bucket" {
  source = "./modules/s3-bucket"

  bucket_name = "${var.fixtures_bucket_name}-${random_id.suffix.hex}"
  kms_key_arn = var.kms_key_arn
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-fixtures"
  })
}

resource "aws_iam_policy" "fixtures_read_only" {
  name        = "${var.project_name}-${var.environment}-fixtures-read-only"
  description = "Allows read-only access to the fixtures S3 bucket"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject"]
      Resource = ["arn:aws:s3:::${var.fixtures_bucket_name}-${random_id.suffix.hex}/*"]
    }]
  })
  tags = var.common_tags
}

module "static_bucket" {
  source = "./modules/s3-bucket"

  bucket_name = "${var.project_name}-${var.environment}-static-${random_id.suffix.hex}"
  kms_key_arn = var.kms_key_arn
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-static"
  })
}

resource "aws_iam_policy" "static_read_write" {
  name        = "${var.project_name}-${var.environment}-static-read-write"
  description = "Allows read/write access to the static files S3 bucket"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ]
      Resource = [
        module.static_bucket.arn,
        "${module.static_bucket.arn}/*"
      ]
    }]
  })
  tags = var.common_tags
}
