mock_provider "aws" {}

variables {
  aws_region            = "us-east-2"
  common_tags           = { Environment = "test", Project = "nest" }
  container_cpu         = 512
  container_memory      = 1024
  container_port        = 3000
  desired_count         = 2
  environment           = "test"
  health_check_path     = "/"
  image_tag             = "test-tag"
  kms_key_arn           = "arn:aws:kms:us-east-2:123456789012:key/12345678-1234-1234-1234-123456789012"
  log_retention_in_days = 7
  parameters_arns       = { "NEXT_PUBLIC_API_URL" = "arn:aws:ssm:us-east-2:123456789012:parameter/nest/test/NEXT_PUBLIC_API_URL" }
  project_name          = "nest"
  security_group_id     = "sg-service-12345"
  service_name          = "service"
  subnet_ids            = ["subnet-1", "subnet-2"]
  target_group_arn      = "arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/nest-test-service-tg/1234567890123456"
}

run "test_cloudwatch_log_group_name_format" {
  command = plan

  assert {
    condition     = aws_cloudwatch_log_group.main.name == "/aws/ecs/${var.project_name}-${var.environment}-${var.service_name}"
    error_message = "CloudWatch log group name must follow format: /aws/ecs/{project}-{environment}-{service_name}."
  }
}

run "test_cloudwatch_log_group_retention" {
  command = plan

  assert {
    condition     = aws_cloudwatch_log_group.main.retention_in_days == var.log_retention_in_days
    error_message = "CloudWatch log group must have correct retention."
  }
}

run "test_ecr_repository_name_format" {
  command = plan

  assert {
    condition     = aws_ecr_repository.main.name == "${var.project_name}-${var.environment}-${var.service_name}"
    error_message = "ECR repository name must follow format: {project}-{environment}-{service_name}."
  }
}

run "test_ecr_repository_scan_on_push_enabled" {
  command = plan

  assert {
    condition     = aws_ecr_repository.main.image_scanning_configuration[0].scan_on_push == true
    error_message = "ECR repository must have scan on push enabled."
  }
}

run "test_ecr_repository_image_tag_mutability" {
  command = plan

  assert {
    condition     = aws_ecr_repository.main.image_tag_mutability == "IMMUTABLE"
    error_message = "ECR repository must have immutable image tags."
  }
}

run "test_ecr_lifecycle_policy_repository" {
  command = plan

  assert {
    condition     = aws_ecr_lifecycle_policy.main.repository == aws_ecr_repository.main.name
    error_message = "ECR lifecycle policy must be attached to the repository."
  }
}

run "test_ecs_cluster_name_format" {
  command = plan

  assert {
    condition     = aws_ecs_cluster.main.name == "${var.project_name}-${var.environment}-${var.service_name}-cluster"
    error_message = "ECS cluster name must follow format: {project}-{environment}-{service_name}-cluster."
  }
}

run "test_ecs_cluster_container_insights_enabled" {
  command = plan

  assert {
    condition     = one([for s in aws_ecs_cluster.main.setting : s.value if s.name == "containerInsights"]) == "enabled"
    error_message = "ECS cluster must have container insights enabled."
  }
}

run "test_task_definition_name_format" {
  command = plan

  assert {
    condition     = aws_ecs_task_definition.main.family == "${var.project_name}-${var.environment}-${var.service_name}"
    error_message = "Task definition family must follow format: {project}-{environment}-{service_name}."
  }
}

run "test_task_definition_cpu" {
  command = plan

  assert {
    condition     = aws_ecs_task_definition.main.cpu == tostring(var.container_cpu)
    error_message = "Task definition CPU must match container_cpu variable."
  }
}

run "test_task_definition_memory" {
  command = plan

  assert {
    condition     = aws_ecs_task_definition.main.memory == tostring(var.container_memory)
    error_message = "Task definition memory must match container_memory variable."
  }
}

run "test_task_definition_has_container_health_check" {
  command = plan

  assert {
    condition     = can(local.container_definition.healthCheck)
    error_message = "Task definition container must include ECS healthCheck configuration."
  }

  assert {
    condition     = local.container_definition.healthCheck.command[0] == "CMD-SHELL"
    error_message = "Health check command must use CMD-SHELL."
  }

  assert {
    condition     = strcontains(local.container_definition.healthCheck.command[1], ":${var.container_port}${var.health_check_path}")
    error_message = "Health check command must target the configured container_port and health_check_path."
  }

  assert {
    condition     = local.container_definition.healthCheck.interval == 30
    error_message = "Health check interval must be 30 seconds."
  }

  assert {
    condition     = local.container_definition.healthCheck.retries == 3
    error_message = "Health check retries must be 3."
  }

  assert {
    condition     = local.container_definition.healthCheck.startPeriod == 100
    error_message = "Health check startPeriod must be 100 seconds."
  }

  assert {
    condition     = local.container_definition.healthCheck.timeout == 5
    error_message = "Health check timeout must be 5 seconds."
  }
}

run "test_task_definition_network_mode" {
  command = plan

  assert {
    condition     = aws_ecs_task_definition.main.network_mode == "awsvpc"
    error_message = "Task definition must use awsvpc network mode."
  }
}

run "test_task_definition_requires_fargate" {
  command = plan

  assert {
    condition     = contains(aws_ecs_task_definition.main.requires_compatibilities, "FARGATE")
    error_message = "Task definition must require FARGATE compatibility."
  }
}

run "test_ecs_service_name_format" {
  command = plan

  assert {
    condition     = aws_ecs_service.main.name == "${var.project_name}-${var.environment}-${var.service_name}-service"
    error_message = "ECS service name must follow format: {project}-{environment}-{service_name}-service."
  }
}

run "test_ecs_service_desired_count" {
  command = plan

  assert {
    condition     = aws_ecs_service.main.desired_count == var.desired_count
    error_message = "ECS service desired count must match variable."
  }
}

run "test_ecs_service_force_new_deployment_disabled_by_default" {
  command = plan

  assert {
    condition     = aws_ecs_service.main.force_new_deployment == false
    error_message = "ECS service force_new_deployment must be false by default."
  }
}

run "test_auto_scaling_disabled_by_default" {
  command = plan

  assert {
    condition     = length(aws_appautoscaling_target.main) == 0
    error_message = "Auto scaling must be disabled by default."
  }
}

run "test_auto_scaling_enabled_when_configured" {
  command = plan

  variables {
    enable_auto_scaling = true
  }

  assert {
    condition     = length(aws_appautoscaling_target.main) == 1
    error_message = "Auto scaling must be enabled when enable_auto_scaling is true."
  }
}

run "test_iam_task_role_name_format" {
  command = plan

  assert {
    condition     = aws_iam_role.ecs_task_role.name == "${var.project_name}-${var.environment}-${var.service_name}-task-role"
    error_message = "Task role name must follow format: {project}-{environment}-{service_name}-task-role."
  }
}

run "test_iam_execution_role_name_format" {
  command = plan

  assert {
    condition     = aws_iam_role.ecs_task_execution_role.name == "${var.project_name}-${var.environment}-${var.service_name}-execution-role"
    error_message = "Execution role name must follow format: {project}-{environment}-{service_name}-execution-role."
  }
}

run "test_iam_role_policy_attachments_link" {
  command = plan

  assert {
    condition     = aws_iam_role_policy_attachment.ecs_task_execution_policy_attachment.role == aws_iam_role.ecs_task_execution_role.name
    error_message = "Main execution policy must be attached to the execution role."
  }

  assert {
    condition     = aws_iam_role_policy_attachment.ecs_task_execution_ssm_policy_attachment.role == aws_iam_role.ecs_task_execution_role.name
    error_message = "SSM execution policy must be attached to the execution role."
  }
}

run "test_service_works_with_backend_config" {
  command = plan

  variables {
    command          = ["./entrypoint.sh"]
    container_cpu    = 1024
    container_memory = 2048
    container_port   = 8000
    service_name     = "backend"
    parameters_arns = {
      "DJANGO_SECRET_KEY" = "arn:aws:ssm:us-east-2:123456789012:parameter/nest/test/DJANGO_SECRET_KEY"
    }
  }

  assert {
    condition     = aws_ecs_cluster.main.name == "${var.project_name}-${var.environment}-backend-cluster"
    error_message = "Service module must work with backend service_name."
  }

  assert {
    condition     = aws_ecr_repository.main.name == "${var.project_name}-${var.environment}-backend"
    error_message = "ECR repository must use backend service_name."
  }

  assert {
    condition     = aws_ecs_task_definition.main.cpu == "1024"
    error_message = "Task definition must use overridden CPU value."
  }

  assert {
    condition     = aws_ecs_task_definition.main.memory == "2048"
    error_message = "Task definition must use overridden memory value."
  }
}

run "test_fargate_spot_capacity_provider" {
  command = plan

  variables {
    use_fargate_spot = true
  }

  assert {
    condition     = one([for s in aws_ecs_cluster_capacity_providers.main.default_capacity_provider_strategy : s.capacity_provider]) == "FARGATE_SPOT"
    error_message = "Cluster must use FARGATE_SPOT when use_fargate_spot is true."
  }
}

run "test_fargate_standard_capacity_provider" {
  command = plan

  variables {
    use_fargate_spot = false
  }

  assert {
    condition     = one([for s in aws_ecs_cluster_capacity_providers.main.default_capacity_provider_strategy : s.capacity_provider]) == "FARGATE"
    error_message = "Cluster must use FARGATE when use_fargate_spot is false."
  }
}
