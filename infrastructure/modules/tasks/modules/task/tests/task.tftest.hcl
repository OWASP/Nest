mock_provider "aws" {}

variables {
  aws_region                   = "us-east-2"
  command                      = ["/bin/sh", "-c", "echo test"]
  common_tags                  = { Environment = "test", Project = "nest" }
  container_parameters_arns    = {}
  cpu                          = "256"
  ecs_cluster_arn              = "arn:aws:ecs:us-east-2:123456789012:cluster/test-cluster"
  ecs_tasks_execution_role_arn = "arn:aws:iam::123456789012:role/test-execution-role"
  environment                  = "test"
  image_url                    = "123456789012.dkr.ecr.us-east-2.amazonaws.com/test:latest"
  kms_key_arn                  = "arn:aws:kms:us-east-2:123456789012:key/12345678-1234-1234-1234-123456789012"
  memory                       = "512"
  project_name                 = "nest"
  security_group_ids           = ["sg-12345678"]
  subnet_ids                   = ["subnet-12345678"]
  task_name                    = "test-task"
}

run "test_task_definition_family_format" {
  command = plan

  assert {
    condition     = aws_ecs_task_definition.task.family == "${var.project_name}-${var.environment}-${var.task_name}"
    error_message = "Task definition family must follow format: {project}-{environment}-{task_name}."
  }
}

run "test_task_definition_network_mode" {
  command = plan

  assert {
    condition     = aws_ecs_task_definition.task.network_mode == "awsvpc"
    error_message = "Task definition must use awsvpc network mode."
  }
}

run "test_task_definition_requires_fargate" {
  command = plan

  assert {
    condition     = contains(aws_ecs_task_definition.task.requires_compatibilities, "FARGATE")
    error_message = "Task definition must require FARGATE compatibility."
  }
}

run "test_task_definition_cpu" {
  command = plan

  assert {
    condition     = aws_ecs_task_definition.task.cpu == var.cpu
    error_message = "Task definition CPU must match variable."
  }
}

run "test_task_definition_memory" {
  command = plan

  assert {
    condition     = aws_ecs_task_definition.task.memory == var.memory
    error_message = "Task definition memory must match variable."
  }
}

run "test_log_group_name_format" {
  command = plan

  assert {
    condition     = aws_cloudwatch_log_group.task.name == "/aws/ecs/${var.project_name}-${var.environment}-${var.task_name}"
    error_message = "Log group name must follow format: /aws/ecs/{project}-{environment}-{task_name}."
  }
}

run "test_log_group_retention" {
  command = plan

  assert {
    condition     = aws_cloudwatch_log_group.task.retention_in_days == 90
    error_message = "Log group retention must be 90 days by default."
  }
}

run "test_log_group_encrypted" {
  command = plan

  assert {
    condition     = aws_cloudwatch_log_group.task.kms_key_id == var.kms_key_arn
    error_message = "Log group must be encrypted with KMS key."
  }
}

run "test_eventbridge_rule_not_created_without_schedule" {
  command = plan

  assert {
    condition     = length(aws_cloudwatch_event_rule.task) == 0
    error_message = "EventBridge rule should not be created when schedule_expression is null."
  }
}

run "test_eventbridge_target_not_created_without_schedule" {
  command = plan

  assert {
    condition     = length(aws_cloudwatch_event_target.task) == 0
    error_message = "EventBridge target should not be created when schedule_expression is null."
  }
}

run "test_eventbridge_rule_created_with_schedule" {
  command = plan

  variables {
    schedule_expression   = "cron(0 12 * * ? *)"
    event_bridge_role_arn = "arn:aws:iam::123456789012:role/test-eventbridge-role"
  }

  assert {
    condition     = length(aws_cloudwatch_event_rule.task) == 1
    error_message = "EventBridge rule should be created when schedule_expression is set."
  }
}

run "test_eventbridge_rule_name_format" {
  command = plan

  variables {
    schedule_expression   = "cron(0 12 * * ? *)"
    event_bridge_role_arn = "arn:aws:iam::123456789012:role/test-eventbridge-role"
  }

  assert {
    condition     = aws_cloudwatch_event_rule.task[0].name == "${var.project_name}-${var.environment}-${var.task_name}-rule"
    error_message = "EventBridge rule name must follow format: {project}-{environment}-{task_name}-rule."
  }
}

run "test_capacity_provider_fargate_default" {
  command = plan

  variables {
    schedule_expression   = "cron(0 12 * * ? *)"
    event_bridge_role_arn = "arn:aws:iam::123456789012:role/test-eventbridge-role"
    use_fargate_spot      = false
  }

  assert {
    condition     = one(aws_cloudwatch_event_target.task[0].ecs_target[0].capacity_provider_strategy).capacity_provider == "FARGATE"
    error_message = "Capacity provider must be FARGATE when use_fargate_spot is false."
  }
}

run "test_capacity_provider_fargate_spot" {
  command = plan

  variables {
    schedule_expression   = "cron(0 12 * * ? *)"
    event_bridge_role_arn = "arn:aws:iam::123456789012:role/test-eventbridge-role"
    use_fargate_spot      = true
  }

  assert {
    condition     = one(aws_cloudwatch_event_target.task[0].ecs_target[0].capacity_provider_strategy).capacity_provider == "FARGATE_SPOT"
    error_message = "Capacity provider must be FARGATE_SPOT when use_fargate_spot is true."
  }
}
