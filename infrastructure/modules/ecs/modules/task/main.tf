terraform {
  required_version = "1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.22.0"
    }
  }
}

resource "aws_cloudwatch_log_group" "task" {
  kms_key_id        = var.kms_key_arn
  name              = "/aws/ecs/${var.project_name}-${var.environment}-${var.task_name}"
  retention_in_days = var.log_retention_in_days
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-${var.task_name}-logs"
  })
}

resource "aws_ecs_task_definition" "task" {
  family                   = "${var.project_name}-${var.environment}-${var.task_name}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.cpu
  memory                   = var.memory
  execution_role_arn       = var.ecs_tasks_execution_role_arn
  task_role_arn            = var.task_role_arn
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-${var.task_name}-task-def"
  })

  container_definitions = jsonencode([
    {
      name      = "backend"
      image     = var.image_url
      command   = var.command
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.task.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
      secrets = [for name, valueFrom in var.container_parameters_arns : {
        name      = name
        valueFrom = valueFrom
      }]
    }
  ])
}

resource "aws_cloudwatch_event_rule" "task" {
  count = var.schedule_expression != null ? 1 : 0

  name                = "${var.project_name}-${var.environment}-${var.task_name}-rule"
  description         = "Fires on a schedule to trigger the ${var.task_name} task"
  schedule_expression = var.schedule_expression
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-${var.task_name}-rule"
  })
}

resource "aws_cloudwatch_event_target" "task" {
  count = var.schedule_expression != null ? 1 : 0

  arn       = var.ecs_cluster_arn
  role_arn  = var.event_bridge_role_arn
  rule      = aws_cloudwatch_event_rule.task[0].name
  target_id = "${var.project_name}-${var.environment}-${var.task_name}-target"

  ecs_target {
    launch_type         = null
    task_definition_arn = aws_ecs_task_definition.task.arn

    capacity_provider_strategy {
      base              = 0
      capacity_provider = var.use_fargate_spot ? "FARGATE_SPOT" : "FARGATE"
      weight            = 1
    }

    network_configuration {
      assign_public_ip = var.assign_public_ip
      security_groups  = var.security_group_ids
      subnets          = var.subnet_ids
    }
  }
}
