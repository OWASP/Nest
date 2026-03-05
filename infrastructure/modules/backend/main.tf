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

resource "aws_cloudwatch_log_group" "backend" {
  kms_key_id        = var.kms_key_arn
  name              = "/aws/ecs/${var.project_name}-${var.environment}-backend"
  retention_in_days = var.log_retention_in_days
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-backend-logs"
  })
}

resource "aws_ecs_cluster" "backend" {
  name = "${var.project_name}-${var.environment}-backend-cluster"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-backend-cluster"
  })

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_cluster_capacity_providers" "backend" {
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]
  cluster_name       = aws_ecs_cluster.backend.name

  default_capacity_provider_strategy {
    base              = 0
    capacity_provider = var.use_fargate_spot ? "FARGATE_SPOT" : "FARGATE"
    weight            = 1
  }
}

resource "aws_ecs_task_definition" "backend" {
  container_definitions = jsonencode([
    {
      command   = ["./entrypoint.sh"]
      essential = true
      image     = var.image_url
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.backend.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
      name = "backend"
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]
      secrets = [for name, valueFrom in var.backend_parameters_arns : {
        name      = name
        valueFrom = valueFrom
      }]
    }
  ])
  cpu                      = var.container_cpu
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  family                   = "${var.project_name}-${var.environment}-backend"
  memory                   = var.container_memory
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-backend-task-def"
  })
  task_role_arn = aws_iam_role.ecs_task_role.arn
}

resource "aws_ecs_service" "backend" {
  cluster                           = aws_ecs_cluster.backend.id
  desired_count                     = var.desired_count
  force_new_deployment              = true
  health_check_grace_period_seconds = 60
  name                              = "${var.project_name}-${var.environment}-backend-service"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-backend-service"
  })
  task_definition = aws_ecs_task_definition.backend.arn

  capacity_provider_strategy {
    base              = 0
    capacity_provider = var.use_fargate_spot ? "FARGATE_SPOT" : "FARGATE"
    weight            = 1
  }

  load_balancer {
    container_name   = "backend"
    container_port   = 8000
    target_group_arn = var.target_group_arn
  }

  network_configuration {
    assign_public_ip = false
    security_groups  = [var.backend_sg_id]
    subnets          = var.private_subnet_ids
  }
}

resource "aws_appautoscaling_target" "backend" {
  count              = var.enable_auto_scaling ? 1 : 0
  max_capacity       = var.max_count
  min_capacity       = var.min_count
  resource_id        = "service/${aws_ecs_cluster.backend.name}/${aws_ecs_service.backend.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "backend_cpu" {
  count              = var.enable_auto_scaling ? 1 : 0
  name               = "${var.project_name}-${var.environment}-backend-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.backend[0].resource_id
  scalable_dimension = aws_appautoscaling_target.backend[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.backend[0].service_namespace

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
  name = "${var.project_name}-${var.environment}-backend-task-role"
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
  name = "${var.project_name}-${var.environment}-backend-execution-role"
  tags = var.common_tags
}

resource "aws_iam_policy" "ecs_task_execution_policy" {
  description = "Policy for ECS task execution - ECR and CloudWatch Logs access."
  name        = "${var.project_name}-${var.environment}-backend-execution-policy"

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
        Resource = var.ecr_repository_arn
      },
      {
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "${aws_cloudwatch_log_group.backend.arn}:*"
      }
    ]
  })
}

resource "aws_iam_policy" "ecs_task_execution_ssm_policy" {
  description = "Policy to allow ECS tasks to read SSM parameters."
  name        = "${var.project_name}-${var.environment}-backend-ssm-policy"

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
