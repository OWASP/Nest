mock_provider "aws" {}

variables {
  app_security_group_ids = ["sg-backend"]
  aws_region             = "us-east-2"
  common_tags            = { Environment = "test", Project = "nest" }
  environment            = "test"
  kms_key_arn            = "arn:aws:kms:us-east-2:123456789012:key/12345678-1234-1234-1234-123456789012"
  project_name           = "nest"
  subnet_ids             = ["subnet-1", "subnet-2"]
  vm_image               = "victoriametrics/victoria-metrics:v1.145.0@sha256:c014fb5a711d38cb24fd0673197592cd1394bb903dbb16aea565620c9c8a3d70"
  vpc_id                 = "vpc-12345"
}

run "grafana_release_repository" {
  command = plan

  assert {
    condition = (
      aws_ecr_repository.grafana.name == "nest-test-grafana" &&
      aws_ecr_repository.grafana.image_tag_mutability == "IMMUTABLE" &&
      aws_ecr_repository.grafana.image_scanning_configuration[0].scan_on_push
    )
    error_message = "Grafana releases must use the environment-scoped repository, immutable tags, and push scanning."
  }

  assert {
    condition = (
      aws_ecr_lifecycle_policy.grafana.repository == aws_ecr_repository.grafana.name &&
      jsondecode(aws_ecr_lifecycle_policy.grafana.policy).rules[0].selection.countNumber == 7
    )
    error_message = "Grafana must use the project's seven-image retention policy."
  }
}

run "grafana_runtime_is_opt_in" {
  command = plan
  assert {
    condition = (
      length(aws_ecs_service.grafana) == 0 &&
      length(aws_ecs_task_definition.grafana) == 0 &&
      length(aws_efs_access_point.grafana) == 0 &&
      length(aws_cloudwatch_log_group.grafana) == 0 &&
      length(aws_security_group.grafana) == 0
    )
    error_message = "No Grafana runtime resources should be created without an image."
  }
}

run "grafana_private_single_instance_runtime" {
  command = plan
  variables {
    grafana_image = "123456789012.dkr.ecr.us-east-2.amazonaws.com/nest-test-grafana@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  }

  assert {
    condition = (
      aws_ecs_service.grafana[0].desired_count == 0 &&
      aws_ecs_service.grafana[0].network_configuration[0].assign_public_ip == false &&
      toset(aws_ecs_service.grafana[0].network_configuration[0].subnets) == toset(var.subnet_ids) &&
      aws_ecs_service.grafana[0].deployment_maximum_percent == 100 &&
      aws_ecs_service.grafana[0].deployment_minimum_healthy_percent == 0 &&
      one(aws_ecs_service.grafana[0].capacity_provider_strategy).capacity_provider == "FARGATE" &&
      aws_ecs_service.grafana[0].deployment_circuit_breaker[0].rollback
    )
    error_message = "Grafana must default to stopped, use private on-demand Fargate, and replace tasks without overlapping writers."
  }

  assert {
    condition = (
      aws_ecs_task_definition.grafana[0].runtime_platform[0].cpu_architecture == "ARM64" &&
      jsondecode(aws_ecs_task_definition.grafana[0].container_definitions)[0].user == "472:472" &&
      jsondecode(aws_ecs_task_definition.grafana[0].container_definitions)[0].image == var.grafana_image &&
      jsondecode(aws_ecs_task_definition.grafana[0].container_definitions)[0].healthCheck.command[1] == "wget --spider -q http://127.0.0.1:3000/api/health || exit 1"
    )
    error_message = "The task must run the supplied ARM64 image as Grafana's non-root user with a health check."
  }

  assert {
    condition = (
      aws_efs_access_point.grafana[0].root_directory[0].path == "/grafana" &&
      aws_efs_access_point.grafana[0].posix_user[0].uid == 472 &&
      aws_efs_access_point.grafana[0].root_directory[0].creation_info[0].permissions == "0700" &&
      one(aws_ecs_task_definition.grafana[0].volume).efs_volume_configuration[0].transit_encryption == "ENABLED" &&
      jsondecode(aws_ecs_task_definition.grafana[0].container_definitions)[0].mountPoints[0].containerPath == "/var/lib/grafana"
    )
    error_message = "Grafana state must use its own restricted EFS path over encrypted NFS."
  }

  assert {
    condition = (
      { for e in local.grafana_container_definition.environment : e.name => e.value }["GF_AUTH_ANONYMOUS_ENABLED"] == "false" &&
      { for e in local.grafana_container_definition.environment : e.name => e.value }["GF_SECURITY_DISABLE_INITIAL_ADMIN_CREATION"] == "true" &&
      { for e in local.grafana_container_definition.environment : e.name => e.value }["O11Y_METRICS_URL"] == "http://victoriametrics.nest-test-observability.internal:8428" &&
      aws_security_group_rule.grafana_to_metrics[0].from_port == 8428 &&
      aws_security_group_rule.metrics_from_grafana[0].type == "ingress"
    )
    error_message = "Grafana must query private service discovery without enabling anonymous access or default admin credentials."
  }
}

run "grafana_rejects_multiple_writers" {
  command = plan
  variables {
    grafana_image         = "example.com/grafana@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    grafana_desired_count = 2
  }
  expect_failures = [var.grafana_desired_count]
}

run "grafana_rejects_mutable_image" {
  command = plan
  variables {
    grafana_image = "example.com/grafana:latest"
  }
  expect_failures = [var.grafana_image]
}

run "grafana_pull_permissions_are_repository_scoped" {
  command = plan

  override_resource {
    target          = aws_ecr_repository.grafana
    override_during = plan
    values = {
      arn            = "arn:aws:ecr:us-east-2:123456789012:repository/nest-test-grafana"
      repository_url = "123456789012.dkr.ecr.us-east-2.amazonaws.com/nest-test-grafana"
    }
  }

  assert {
    condition = (
      length(jsondecode(aws_iam_policy.grafana_image_pull.policy).Statement) == 2 &&
      jsondecode(aws_iam_policy.grafana_image_pull.policy).Statement[0].Action == "ecr:GetAuthorizationToken" &&
      jsondecode(aws_iam_policy.grafana_image_pull.policy).Statement[0].Resource == "*" &&
      toset(jsondecode(aws_iam_policy.grafana_image_pull.policy).Statement[1].Action) == toset([
        "ecr:BatchCheckLayerAvailability", "ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"
      ]) &&
      jsondecode(aws_iam_policy.grafana_image_pull.policy).Statement[1].Resource == aws_ecr_repository.grafana.arn
    )
    error_message = "Only token authentication may use a wildcard; image access must be pull-only and limited to Grafana's repository."
  }

  assert {
    condition = (
      jsondecode(aws_iam_role.grafana_execution.assume_role_policy).Statement[0].Principal.Service == "ecs-tasks.amazonaws.com" &&
      aws_iam_role_policy_attachment.grafana_image_pull.role == aws_iam_role.grafana_execution.name
    )
    error_message = "Image pull permissions must belong to the dedicated Grafana ECS execution role."
  }

  assert {
    condition = (
      output.grafana_ecr_repository_arn == aws_ecr_repository.grafana.arn &&
      output.grafana_ecr_repository_url == aws_ecr_repository.grafana.repository_url
    )
    error_message = "Repository outputs must identify Grafana's release repository."
  }
}
