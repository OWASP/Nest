mock_provider "aws" {}

variables {
  task_context = {
    cluster_arn        = "arn:aws:ecs:us-east-2:123456789012:cluster/nest-test-nestbot-cluster"
    execution_role_arn = "arn:aws:iam::123456789012:role/nest-test-nestbot-execution-role"
    task_role_arn      = "arn:aws:iam::123456789012:role/nest-test-nestbot-task-role"
    cpu                = 1024
    memory             = 2048
    container_definition = {
      name         = "nestbot"
      image        = "example.invalid/nestbot:test"
      essential    = true
      command      = ["./entrypoint.nestbot.sh"]
      stopTimeout  = 60
      portMappings = [{ containerPort = 8000, hostPort = 8000, protocol = "tcp" }]
      environment  = [{ name = "DJANGO_NESTBOT_AI_ASSISTANT_ENABLED", value = "false" }]
      secrets      = [{ name = "DJANGO_SECRET_KEY", valueFrom = "arn:aws:ssm:us-east-2:123456789012:parameter/nest/test/DJANGO_SECRET_KEY" }]
      healthCheck = {
        command     = ["CMD", "web-health"]
        interval    = 30
        retries     = 3
        startPeriod = 100
        timeout     = 5
      }
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/aws/ecs/nest-test-nestbot"
          awslogs-region        = "us-east-2"
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  }
  name_prefix          = "nest-test-nestbot-worker"
  container_name       = "nestbot-worker"
  command              = ["python", "manage.py", "rqworker", "ai", "--with-scheduler", "--worker-ttl", "90"]
  health_check_command = ["CMD", "python", "manage.py", "slack_ai_worker_healthcheck", "--settings=settings.nestbot_healthcheck"]
  desired_count        = 1
  private_subnet_ids   = ["subnet-1", "subnet-2"]
  security_group_id    = "sg-worker"
}

run "test_worker_preserves_release_and_settings" {
  command = plan
  assert {
    condition     = local.container_definition.image == var.task_context.container_definition.image && local.container_definition.environment == var.task_context.container_definition.environment && local.container_definition.secrets == var.task_context.container_definition.secrets && local.container_definition.stopTimeout == 60
    error_message = "Workers must inherit the image, settings, secrets and stop timeout."
  }
  assert {
    condition     = local.container_definition.name == "nestbot-worker" && local.container_definition.command == var.command && local.container_definition.healthCheck.command == var.health_check_command && length(local.container_definition.portMappings) == 0 && local.container_definition.logConfiguration.options["awslogs-stream-prefix"] == "worker"
    error_message = "Workers must use their own command, probe and log stream without web ports."
  }
  assert {
    condition     = aws_ecs_task_definition.main.execution_role_arn == var.task_context.execution_role_arn && aws_ecs_task_definition.main.task_role_arn == var.task_context.task_role_arn && aws_ecs_task_definition.main.cpu == "1024" && aws_ecs_task_definition.main.memory == "2048" && one(aws_ecs_task_definition.main.runtime_platform).cpu_architecture == "ARM64"
    error_message = "Workers must reuse the parent roles and task size on ARM64."
  }
  assert {
    condition     = aws_ecs_task_definition.main.family == "nest-test-nestbot-worker" && aws_ecs_service.main.name == "nest-test-nestbot-worker-service" && aws_ecs_service.main.cluster == var.task_context.cluster_arn && aws_ecs_service.main.desired_count == 1 && length(aws_ecs_service.main.load_balancer) == 0
    error_message = "The worker must have its own service in the parent cluster without an ALB."
  }
  assert {
    condition     = !one(aws_ecs_service.main.network_configuration).assign_public_ip && one(aws_ecs_service.main.network_configuration).subnets == toset(var.private_subnet_ids) && one(aws_ecs_service.main.network_configuration).security_groups == toset([var.security_group_id])
    error_message = "Worker networking must remain private."
  }
}

run "test_worker_bootstrap" {
  command = plan
  variables {
    desired_count = 0
  }
  assert {
    condition     = aws_ecs_service.main.desired_count == 0
    error_message = "Bootstrap must not start worker tasks."
  }
}

run "test_worker_spot_capacity" {
  command = plan
  variables {
    use_fargate_spot = true
  }
  assert {
    condition     = one(aws_ecs_service.main.capacity_provider_strategy).capacity_provider == "FARGATE_SPOT"
    error_message = "The reusable worker must support the selected capacity provider."
  }
}

run "test_reject_empty_health_command" {
  command = plan
  variables {
    health_check_command = []
  }
  expect_failures = [var.health_check_command]
}

run "test_reject_blank_health_command" {
  command = plan
  variables {
    health_check_command = ["CMD-SHELL", ""]
  }
  expect_failures = [var.health_check_command]
}

run "test_reject_whitespace_health_command" {
  command = plan
  variables {
    health_check_command = ["CMD-SHELL", " \t\n"]
  }
  expect_failures = [var.health_check_command]
}

run "test_reject_null_health_command" {
  command = plan
  variables {
    health_check_command = ["CMD", null]
  }
  expect_failures = [var.health_check_command]
}

run "test_reject_prefix_health_command" {
  command = plan
  variables {
    health_check_command = ["INVALID", "true"]
  }
  expect_failures = [var.health_check_command]
}
