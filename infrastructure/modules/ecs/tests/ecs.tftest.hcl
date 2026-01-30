mock_provider "aws" {}

variables {
  aws_region                    = "us-east-2"
  common_tags                   = { Environment = "test", Project = "nest" }
  container_parameters_arns     = {}
  ecs_sg_id                     = "sg-12345678"
  environment                   = "test"
  fixtures_bucket_name          = "nest-fixtures-abcd1234"
  fixtures_read_only_policy_arn = "arn:aws:iam::123456789012:policy/test-fixtures-policy"
  kms_key_arn                   = "arn:aws:kms:us-east-2:123456789012:key/12345678-1234-1234-1234-123456789012"
  project_name                  = "nest"
  subnet_ids                    = ["subnet-12345678"]
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

run "test_ecr_repository_name_format" {
  command = plan

  assert {
    condition     = aws_ecr_repository.main.name == "${var.project_name}-${var.environment}-backend"
    error_message = "ECR repository name must follow format: {project}-{environment}-backend."
  }
}

run "test_ecr_scan_on_push" {
  command = plan

  assert {
    condition     = aws_ecr_repository.main.image_scanning_configuration[0].scan_on_push == true
    error_message = "ECR repository must have scan on push enabled."
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
