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

data "aws_iam_policy_document" "fixtures_read_only" {
  statement {
    actions = [
      "s3:GetObject"
    ]
    effect = "Allow"
    resources = [
      "arn:aws:s3:::${var.fixtures_bucket_name}-${random_id.suffix.hex}/*"
    ]
  }
}

resource "random_id" "suffix" {
  byte_length = 4
}

module "fixtures_bucket" {
  source = "./modules/s3-bucket"

  bucket_name = "${var.fixtures_bucket_name}-${random_id.suffix.hex}"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-fixtures"
  })
}

module "zappa_bucket" {
  source = "./modules/s3-bucket"

  bucket_name = "${var.zappa_bucket_name}-${random_id.suffix.hex}"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-zappa-deployments"
  })
}

resource "aws_iam_policy" "fixtures_read_only" {
  name        = "${var.project_name}-${var.environment}-fixtures-read-only"
  description = "Allows read-only access to the fixtures S3 bucket"
  policy      = data.aws_iam_policy_document.fixtures_read_only.json
  tags        = var.common_tags
}
