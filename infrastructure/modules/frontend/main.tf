terraform {
  required_version = "1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.22.0"
    }
  }
}

data "aws_caller_identity" "current" {}

resource "aws_cloudwatch_log_group" "frontend" {
  kms_key_id        = var.kms_key_arn
  name              = "/aws/ecs/${var.project_name}-${var.environment}-frontend"
  retention_in_days = var.log_retention_in_days
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-frontend-logs"
  })
}

# TODO: disallow tag mutability
# nosemgrep: terraform.aws.security.aws-ecr-mutable-image-tags.aws-ecr-mutable-image-tags
resource "aws_ecr_repository" "frontend" {
  image_tag_mutability = "MUTABLE"
  name                 = "${var.project_name}-${var.environment}-frontend"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-frontend-ecr"
  })

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_lifecycle_policy" "frontend" {
  policy = jsonencode({
    rules = [
      {
        action = {
          type = "expire"
        }
        description  = "Expire untagged images after 7 days."
        rulePriority = 1
        selection = {
          countNumber = 7
          countType   = "sinceImagePushed"
          countUnit   = "days"
          tagStatus   = "untagged"
        }
      }
    ]
  })
  repository = aws_ecr_repository.frontend.name
}

resource "aws_ecs_cluster" "frontend" {
  name = "${var.project_name}-${var.environment}-frontend-cluster"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-frontend-cluster"
  })

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_task_definition" "frontend" {
  container_definitions = jsonencode([
    {
      essential = true
      image     = "${aws_ecr_repository.frontend.repository_url}:${var.image_tag}"
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.frontend.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
      name = "frontend"
      portMappings = [
        {
          containerPort = 3000
          hostPort      = 3000
          protocol      = "tcp"
        }
      ]
      secrets = [for name, valueFrom in var.frontend_parameters_arns : {
        name      = name
        valueFrom = valueFrom
      }]
    }
  ])
  cpu                      = var.container_cpu
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  family                   = "${var.project_name}-${var.environment}-frontend"
  memory                   = var.container_memory
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-frontend-task-def"
  })
  task_role_arn = aws_iam_role.ecs_task_role.arn
}

resource "aws_ecs_service" "frontend" {
  cluster                           = aws_ecs_cluster.frontend.id
  desired_count                     = var.desired_count
  health_check_grace_period_seconds = 60
  name                              = "${var.project_name}-${var.environment}-frontend-service"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-frontend-service"
  })
  task_definition = aws_ecs_task_definition.frontend.arn

  capacity_provider_strategy {
    base              = 0
    capacity_provider = var.use_fargate_spot ? "FARGATE_SPOT" : "FARGATE"
    weight            = 1
  }

  load_balancer {
    container_name   = "frontend"
    container_port   = 3000
    target_group_arn = var.target_group_arn
  }

  network_configuration {
    assign_public_ip = false
    security_groups  = [var.frontend_sg_id]
    subnets          = var.private_subnet_ids
  }
}

resource "aws_appautoscaling_target" "frontend" {
  count              = var.enable_auto_scaling ? 1 : 0
  max_capacity       = var.max_count
  min_capacity       = var.min_count
  resource_id        = "service/${aws_ecs_cluster.frontend.name}/${aws_ecs_service.frontend.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "frontend_cpu" {
  count              = var.enable_auto_scaling ? 1 : 0
  name               = "${var.project_name}-${var.environment}-frontend-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.frontend[0].resource_id
  scalable_dimension = aws_appautoscaling_target.frontend[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.frontend[0].service_namespace

  target_tracking_scaling_policy_configuration {
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
    target_value       = 70.0

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
  }
}

resource "aws_iam_role" "ecs_task_role" {
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
  name = "${var.project_name}-${var.environment}-frontend-task-role"
  tags = var.common_tags
}

resource "aws_iam_role" "ecs_task_execution_role" {
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
  name = "${var.project_name}-${var.environment}-frontend-execution-role"
  tags = var.common_tags
}

resource "aws_iam_policy" "ecs_task_execution_policy" {
  description = "Policy for ECS task execution - ECR and CloudWatch Logs access."
  name        = "${var.project_name}-${var.environment}-frontend-execution-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # https://docs.aws.amazon.com/AmazonECR/latest/public/public-repository-policies.html#repository-policy-vs-iam-policy
        # nosemgrep: terraform.lang.security.iam.no-iam-creds-exposure.no-iam-creds-exposure
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
        Resource = aws_ecr_repository.frontend.arn
      },
      {
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "${aws_cloudwatch_log_group.frontend.arn}:*"
      }
    ]
  })
}

resource "aws_iam_policy" "ecs_task_execution_ssm_policy" {
  description = "Policy to allow ECS tasks to read SSM parameters."
  name        = "${var.project_name}-${var.environment}-frontend-ssm-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/${var.project_name}/${var.environment}/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy_attachment" {
  policy_arn = aws_iam_policy.ecs_task_execution_policy.arn
  role       = aws_iam_role.ecs_task_execution_role.name
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_ssm_policy_attachment" {
  policy_arn = aws_iam_policy.ecs_task_execution_ssm_policy.arn
  role       = aws_iam_role.ecs_task_execution_role.name
}
