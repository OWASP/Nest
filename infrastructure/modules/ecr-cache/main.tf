terraform {
  required_version = "~> 1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.36.0"
    }
  }
}

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
