resource "aws_ecr_repository" "grafana" {
  image_tag_mutability = "IMMUTABLE"
  name                 = "${var.project_name}-${var.environment}-grafana"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-grafana-ecr"
  })

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_lifecycle_policy" "grafana" {
  repository = aws_ecr_repository.grafana.name
  policy = jsonencode({
    rules = [
      {
        action = {
          type = "expire"
        }
        description  = "Keep only the last 7 images."
        rulePriority = 1
        selection = {
          countNumber = 7
          countType   = "imageCountMoreThan"
          tagStatus   = "any"
        }
      }
    ]
  })
}

resource "aws_iam_role" "grafana_execution" {
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
  name = "${local.name_prefix}-grafana-execution-role"
  tags = var.common_tags
}

resource "aws_iam_policy" "grafana_image_pull" {
  description = "Allow the Grafana ECS execution role to pull its container image."
  name        = "${local.name_prefix}-grafana-image-pull"
  tags        = var.common_tags

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # ECR authorization tokens cannot be scoped to a repository ARN.
        # NOSEMGREP: terraform.lang.security.iam.no-iam-creds-exposure.no-iam-creds-exposure
        Action   = "ecr:GetAuthorizationToken"
        Effect   = "Allow"
        Resource = "*" # NOSONAR
      },
      {
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer"
        ]
        Effect   = "Allow"
        Resource = aws_ecr_repository.grafana.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "grafana_image_pull" {
  policy_arn = aws_iam_policy.grafana_image_pull.arn
  role       = aws_iam_role.grafana_execution.name
}
