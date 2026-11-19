terraform {
  required_version = "~> 1.16.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.67.0"
    }
  }
}

locals {
  base_container_definition = var.task_context.container_definition
  container_definition = merge(local.base_container_definition, {
    command      = var.command
    name         = var.container_name
    portMappings = []
    healthCheck = merge(local.base_container_definition.healthCheck, {
      command = var.health_check_command
    })
    logConfiguration = merge(local.base_container_definition.logConfiguration, {
      options = merge(local.base_container_definition.logConfiguration.options, {
        "awslogs-stream-prefix" = "worker"
      })
    })
  })
}

resource "aws_ecs_task_definition" "main" {
  container_definitions    = jsonencode([local.container_definition])
  cpu                      = var.task_context.cpu
  execution_role_arn       = var.task_context.execution_role_arn
  family                   = var.name_prefix
  memory                   = var.task_context.memory
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  task_role_arn            = var.task_context.task_role_arn
  tags                     = var.common_tags

  runtime_platform {
    cpu_architecture        = "ARM64"
    operating_system_family = "LINUX"
  }
}

resource "aws_ecs_service" "main" {
  cluster              = var.task_context.cluster_arn
  desired_count        = var.desired_count
  force_new_deployment = var.force_new_deployment
  name                 = "${var.name_prefix}-service"
  task_definition      = aws_ecs_task_definition.main.arn
  tags                 = var.common_tags

  capacity_provider_strategy {
    base              = 0
    capacity_provider = var.use_fargate_spot ? "FARGATE_SPOT" : "FARGATE"
    weight            = 1
  }

  network_configuration {
    assign_public_ip = false
    security_groups  = [var.security_group_id]
    subnets          = var.private_subnet_ids
  }
}
