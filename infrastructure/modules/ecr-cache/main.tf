terraform {
  required_version = "~> 1.14.0"

  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

# BuildKit registry cache reuses a single tag (e.g. :cache) and overwrites it each build.
# App release images use IMMUTABLE repos with scan-on-push in modules/service; this repo is cache-only.
# NOSEMGREP: terraform.aws.security.aws-ecr-mutable-image-tags.aws-ecr-mutable-image-tags, terraform.lang.security.ecr-image-scan-on-push.ecr-image-scan-on-push
resource "aws_ecr_repository" "main" {
  image_tag_mutability = "MUTABLE"
  name                 = var.name

  tags = merge(var.common_tags, {
    Name = "${var.name}-ecr"
  })

  image_scanning_configuration {
    scan_on_push = false
  }
}

resource "aws_ecr_lifecycle_policy" "main" {
  policy = jsonencode({
    rules = [
      {
        action = {
          type = "expire"
        }
        description  = "Keep the last 3 build cache images."
        rulePriority = 1
        selection = {
          countNumber = 3
          countType   = "imageCountMoreThan"
          tagStatus   = "any"
        }
      }
    ]
  })
  repository = aws_ecr_repository.main.name
}
