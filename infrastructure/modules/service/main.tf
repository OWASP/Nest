terraform {
  required_version = "~> 1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.36.0"
    }
  }
}

locals {
  name_prefix = "${var.project_name}-${var.environment}-${var.service_name}"

  container_definition = merge(
    {
      essential = true
      image     = "${aws_ecr_repository.main.repository_url}:${var.image_tag}"
      healthCheck = {
        command     = ["CMD-SHELL", "wget -qO- http://localhost:${var.container_port}${var.health_check_path} > /dev/null 2>&1 || exit 1"]
        interval    = 30
        retries     = 3
        startPeriod = 60
        timeout     = 5
      }
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.main.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
      name = var.service_name
      portMappings = [
        {
          containerPort = var.container_port
          hostPort      = var.container_port
          protocol      = "tcp"
        }
      ]
      secrets = [for name, valueFrom in var.parameters_arns : {
        name      = name
        valueFrom = valueFrom
      }]
    },
    var.command != null ? { command = var.command } : {}
  )
}

data "aws_caller_identity" "current" {}

resource "aws_cloudwatch_log_group" "main" {
  kms_key_id        = var.kms_key_arn
  name              = "/aws/ecs/${local.name_prefix}"
  retention_in_days = var.log_retention_in_days
  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-logs"
  })
}

resource "aws_ecr_repository" "main" {
  image_tag_mutability = "IMMUTABLE"
  name                 = local.name_prefix
  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-ecr"
  })

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_lifecycle_policy" "main" {
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
  repository = aws_ecr_repository.main.name
}

resource "aws_ecs_cluster" "main" {
  name = "${local.name_prefix}-cluster"
  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-cluster"
  })

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_cluster_capacity_providers" "main" {
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]
  cluster_name       = aws_ecs_cluster.main.name

  default_capacity_provider_strategy {
    base              = 0
    capacity_provider = var.use_fargate_spot ? "FARGATE_SPOT" : "FARGATE"
    weight            = 1
  }
}

resource "aws_ecs_task_definition" "main" {
  container_definitions    = jsonencode([local.container_definition])
  cpu                      = var.container_cpu
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  family                   = local.name_prefix
  memory                   = var.container_memory
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-task-def"
  })
  task_role_arn = aws_iam_role.ecs_task_role.arn
}

resource "aws_ecs_service" "main" {
  cluster                           = aws_ecs_cluster.main.id
  desired_count                     = var.desired_count
  force_new_deployment              = var.force_new_deployment
  health_check_grace_period_seconds = 60
  name                              = "${local.name_prefix}-service"
  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-service"
  })
  task_definition = aws_ecs_task_definition.main.arn

  capacity_provider_strategy {
    base              = 0
    capacity_provider = var.use_fargate_spot ? "FARGATE_SPOT" : "FARGATE"
    weight            = 1
  }

  load_balancer {
    container_name   = var.service_name
    container_port   = var.container_port
    target_group_arn = var.target_group_arn
  }

  network_configuration {
    assign_public_ip = var.assign_public_ip
    security_groups  = [var.security_group_id]
    subnets          = var.subnet_ids
  }
}

resource "aws_appautoscaling_target" "main" {
  count              = var.enable_auto_scaling ? 1 : 0
  max_capacity       = var.max_count
  min_capacity       = var.min_count
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.main.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "cpu" {
  count              = var.enable_auto_scaling ? 1 : 0
  name               = "${local.name_prefix}-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.main[0].resource_id
  scalable_dimension = aws_appautoscaling_target.main[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.main[0].service_namespace

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
  name = "${local.name_prefix}-task-role"
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
  name = "${local.name_prefix}-execution-role"
  tags = var.common_tags
}

resource "aws_iam_policy" "ecs_task_execution_policy" {
  description = "Policy for ECS task execution - ECR and CloudWatch Logs access."
  name        = "${local.name_prefix}-execution-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # https://docs.aws.amazon.com/AmazonECR/latest/public/public-repository-policies.html#repository-policy-vs-iam-policy
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
        Resource = aws_ecr_repository.main.arn
      },
      {
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "${aws_cloudwatch_log_group.main.arn}:*"
      }
    ]
  })
}

resource "aws_iam_policy" "ecs_task_execution_ssm_policy" {
  description = "Policy to allow ECS tasks to read SSM parameters."
  name        = "${local.name_prefix}-ssm-policy"

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

resource "aws_iam_role_policy_attachment" "task_role_policies" {
  for_each   = { for i, arn in var.task_role_policy_arns : "policy-${i}" => arn }
  policy_arn = each.value
  role       = aws_iam_role.ecs_task_role.name
}

resource "aws_iam_policy" "ecs_task_role_kms" {
  description = "Allow ECS task role to use KMS key for encryption and decryption"
  name        = "${local.name_prefix}-task-kms-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey*",
        ]
        Effect   = "Allow"
        Resource = var.kms_key_arn
      }
    ]
  })
  tags = var.common_tags
}

resource "aws_iam_role_policy_attachment" "ecs_task_role_kms" {
  policy_arn = aws_iam_policy.ecs_task_role_kms.arn
  role       = aws_iam_role.ecs_task_role.name
}
