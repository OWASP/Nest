mock_provider "aws" {}

variables {
  aws_region                    = "us-east-2"
  common_tags                   = { Environment = "test", Project = "nest" }
  container_parameters_arns     = {}
  ecr_repository_arn            = "arn:aws:ecr:us-east-2:123456789012:repository/nest-test-backend"
  ecr_repository_url            = "123456789012.dkr.ecr.us-east-2.amazonaws.com/nest-test-backend"
  ecs_sg_id                     = "sg-12345678"
  enable_cron_tasks             = true
  environment                   = "test"
  fixtures_bucket_name          = "nest-fixtures-abcd1234"
  fixtures_read_only_policy_arn = "arn:aws:iam::123456789012:policy/test-fixtures-policy"
  image_tag                     = "test-tag"
  kms_key_arn                   = "arn:aws:kms:us-east-2:123456789012:key/12345678-1234-1234-1234-123456789012"
  project_name                  = "nest"
  subnet_ids                    = ["subnet-12345678"]
}

run "test_cron_tasks_disabled_removes_schedules" {
  command = plan

  variables {
    enable_cron_tasks = false
  }

  assert {
    condition     = local.sync_data_schedule_expression == null
    error_message = "sync_data_schedule_expression must be null when enable_cron_tasks is false."
  }

  assert {
    condition     = local.update_project_health_metrics_schedule_expression == null
    error_message = "update_project_health_metrics_schedule_expression must be null when enable_cron_tasks is false."
  }

  assert {
    condition     = local.update_project_health_scores_schedule_expression == null
    error_message = "update_project_health_scores_schedule_expression must be null when enable_cron_tasks is false."
  }
}

run "test_cron_tasks_enabled_creates_schedules" {
  command = plan

  variables {
    enable_cron_tasks = true
  }

  assert {
    condition     = local.sync_data_schedule_expression == "cron(17 05 * * ? *)"
    error_message = "sync_data_schedule_expression must be set when enable_cron_tasks is true."
  }

  assert {
    condition     = local.update_project_health_metrics_schedule_expression == "cron(17 17 * * ? *)"
    error_message = "update_project_health_metrics_schedule_expression must be set when enable_cron_tasks is true."
  }

  assert {
    condition     = local.update_project_health_scores_schedule_expression == "cron(22 17 * * ? *)"
    error_message = "update_project_health_scores_schedule_expression must be set when enable_cron_tasks is true."
  }
}

run "test_ecs_cluster_name_format" {
  command = plan

  assert {
    condition     = aws_ecs_cluster.main.name == "${var.project_name}-${var.environment}-tasks-cluster"
    error_message = "ECS cluster name must follow format: {project}-{environment}-tasks-cluster."
  }
}

run "test_ecs_capacity_providers" {
  command = plan

  assert {
    condition     = contains(aws_ecs_cluster_capacity_providers.main.capacity_providers, "FARGATE")
    error_message = "ECS cluster must have FARGATE capacity provider."
  }
}

run "test_ecs_capacity_providers_spot" {
  command = plan

  assert {
    condition     = contains(aws_ecs_cluster_capacity_providers.main.capacity_providers, "FARGATE_SPOT")
    error_message = "ECS cluster must have FARGATE_SPOT capacity provider."
  }
}


run "test_ecs_execution_role_name_format" {
  command = plan

  assert {
    condition     = aws_iam_role.ecs_tasks_execution_role.name == "${var.project_name}-${var.environment}-ecs-tasks-execution-role"
    error_message = "ECS execution role name must follow format: {project}-{environment}-ecs-tasks-execution-role."
  }
}

run "test_ecs_task_role_name_format" {
  command = plan

  assert {
    condition     = aws_iam_role.ecs_task_role.name == "${var.project_name}-${var.environment}-ecs-task-role"
    error_message = "ECS task role name must follow format: {project}-{environment}-ecs-task-role."
  }
}

run "test_eventbridge_role_name_format" {
  command = plan

  assert {
    condition     = aws_iam_role.event_bridge_role.name == "${var.project_name}-${var.environment}-event-bridge-role"
    error_message = "EventBridge role name must follow format: {project}-{environment}-event-bridge-role."
  }
}

run "test_ecs_ssm_policy_name_format" {
  command = plan

  assert {
    condition     = aws_iam_policy.ecs_tasks_execution_role_ssm_policy.name == "${var.project_name}-${var.environment}-ecs-tasks-ssm-policy"
    error_message = "ECS SSM policy name must follow format: {project}-{environment}-ecs-tasks-ssm-policy."
  }
}

run "test_ecs_execution_policy_name_format" {
  command = plan

  assert {
    condition     = aws_iam_policy.ecs_tasks_execution_policy.name == "${var.project_name}-${var.environment}-ecs-tasks-execution-policy"
    error_message = "ECS execution policy name must follow format: {project}-{environment}-ecs-tasks-execution-policy."
  }
}

run "test_eventbridge_policy_name_format" {
  command = plan

  assert {
    condition     = aws_iam_policy.event_bridge_ecs_policy.name == "${var.project_name}-${var.environment}-event-bridge-ecs-policy"
    error_message = "EventBridge policy name must follow format: {project}-{environment}-event-bridge-ecs-policy."
  }
}
