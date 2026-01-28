variables {
  aws_region               = "us-east-2"
  common_tags              = { Environment = "test", Project = "nest" }
  container_cpu            = 512
  container_memory         = 1024
  desired_count            = 2
  environment              = "test"
  frontend_parameters_arns = { "NEXT_PUBLIC_API_URL" = "arn:aws:ssm:us-east-2:123456789012:parameter/nest/test/NEXT_PUBLIC_API_URL" }
  frontend_sg_id           = "sg-frontend-12345"
  kms_key_arn           = "arn:aws:kms:us-east-2:123456789012:key/12345678-1234-1234-1234-123456789012"
  log_retention_in_days    = 7
  private_subnet_ids       = ["subnet-private-1", "subnet-private-2"]
  project_name             = "nest"
  target_group_arn         = "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/nest-test-frontend-tg/1234567890123456"
}

run "test_frontend_cloudwatch_log_group_name_format" {
  command = plan

  assert {
    condition     = aws_cloudwatch_log_group.frontend.name == "/aws/ecs/${var.project_name}-${var.environment}-frontend"
    error_message = "CloudWatch log group name must follow format: /aws/ecs/{project}-{environment}-frontend."
  }
}

run "test_frontend_cloudwatch_log_group_retention" {
  command = plan

  assert {
    condition     = aws_cloudwatch_log_group.frontend.retention_in_days == var.log_retention_in_days
    error_message = "CloudWatch log group must have correct retention."
  }
}

run "test_frontend_ecr_repository_name_format" {
  command = plan

  assert {
    condition     = aws_ecr_repository.frontend.name == "${var.project_name}-${var.environment}-frontend"
    error_message = "ECR repository name must follow format: {project}-{environment}-frontend."
  }
}

run "test_frontend_ecr_repository_scan_on_push_enabled" {
  command = plan

  assert {
    condition     = aws_ecr_repository.frontend.image_scanning_configuration[0].scan_on_push == true
    error_message = "ECR repository must have scan on push enabled."
  }
}

run "test_frontend_ecr_repository_image_tag_mutability" {
  command = plan

  assert {
    condition     = aws_ecr_repository.frontend.image_tag_mutability == "MUTABLE"
    error_message = "ECR repository must have mutable image tags."
  }
}

run "test_frontend_ecr_lifecycle_policy_repository" {
  command = plan

  assert {
    condition     = aws_ecr_lifecycle_policy.frontend.repository == aws_ecr_repository.frontend.name
    error_message = "ECR lifecycle policy must be attached to the frontend repository."
  }
}

run "test_frontend_ecs_cluster_name_format" {
  command = plan

  assert {
    condition     = aws_ecs_cluster.frontend.name == "${var.project_name}-${var.environment}-frontend-cluster"
    error_message = "ECS cluster name must follow format: {project}-{environment}-frontend-cluster."
  }
}

run "test_frontend_task_definition_name_format" {
  command = plan

  assert {
    condition     = aws_ecs_task_definition.frontend.family == "${var.project_name}-${var.environment}-frontend"
    error_message = "Task definition must follow format: {project}-{environment}-frontend."
  }
}

run "test_frontend_task_definition_cpu" {
  command = plan

  assert {
    condition     = aws_ecs_task_definition.frontend.cpu == tostring(var.container_cpu)
    error_message = "Task definition CPU must match container_cpu variable."
  }
}

run "test_frontend_task_definition_memory" {
  command = plan

  assert {
    condition     = aws_ecs_task_definition.frontend.memory == tostring(var.container_memory)
    error_message = "Task definition memory must match container_memory variable."
  }
}

run "test_frontend_task_definition_network_mode" {
  command = plan

  assert {
    condition     = aws_ecs_task_definition.frontend.network_mode == "awsvpc"
    error_message = "Task definition must use awsvpc network mode."
  }
}

run "test_frontend_task_definition_requires_fargate" {
  command = plan

  assert {
    condition     = contains(aws_ecs_task_definition.frontend.requires_compatibilities, "FARGATE")
    error_message = "Task definition must require FARGATE compatibility."
  }
}

run "test_frontend_ecs_service_desired_count" {
  command = plan

  assert {
    condition     = aws_ecs_service.frontend.desired_count == var.desired_count
    error_message = "ECS service desired count must match variable."
  }
}

run "test_frontend_auto_scaling_disabled_by_default" {
  command = plan

  assert {
    condition     = length(aws_appautoscaling_target.frontend) == 0
    error_message = "Auto scaling must be disabled by default."
  }
}

run "test_frontend_auto_scaling_enabled_when_configured" {
  command = plan

  variables {
    enable_auto_scaling = true
  }

  assert {
    condition     = length(aws_appautoscaling_target.frontend) == 1
    error_message = "Auto scaling must be enabled when enable_auto_scaling is true."
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
