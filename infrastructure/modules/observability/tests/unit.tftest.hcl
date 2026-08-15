mock_provider "aws" {}

variables {
  app_security_group_ids = ["sg-backend", "sg-frontend", "sg-tasks"]
  aws_region             = "us-east-2"
  common_tags            = { Environment = "test", Project = "nest" }
  environment            = "test"
  kms_key_arn            = "arn:aws:kms:us-east-2:123456789012:key/12345678-1234-1234-1234-123456789012"
  project_name           = "nest"
  subnet_ids             = ["subnet-1", "subnet-2"]
  vm_image               = "victoriametrics/victoria-metrics:v1.145.0@sha256:c014fb5a711d38cb24fd0673197592cd1394bb903dbb16aea565620c9c8a3d70"
  vm_port                = 8428
  vpc_id                 = "vpc-12345"
}

run "test_efs_encryption_enabled" {
  command = plan

  assert {
    condition     = aws_efs_file_system.vm.encrypted == true
    error_message = "EFS must be encrypted at rest."
  }
}

run "test_efs_uses_kms_key" {
  command = plan

  assert {
    condition     = aws_efs_file_system.vm.kms_key_id == var.kms_key_arn
    error_message = "EFS must be encrypted with the provided KMS key."
  }
}

run "test_efs_mount_target_per_subnet" {
  command = plan

  assert {
    condition     = length(aws_efs_mount_target.vm) == length(var.subnet_ids)
    error_message = "There must be one EFS mount target per subnet."
  }
}

run "test_vm_ingest_rule_per_app_security_group" {
  command = plan

  assert {
    condition     = length(aws_security_group_rule.vm_ingest_from_apps) == length(var.app_security_group_ids)
    error_message = "There must be one VM ingest rule per application security group."
  }
}

run "test_vm_ingest_from_source_security_group_only" {
  command = plan

  assert {
    condition     = aws_security_group_rule.vm_ingest_from_apps["sg-backend"].source_security_group_id == "sg-backend"
    error_message = "VM ingest must be restricted to application security groups, not public CIDRs."
  }

  assert {
    condition     = aws_security_group_rule.vm_ingest_from_apps["sg-backend"].from_port == var.vm_port
    error_message = "VM ingest must be allowed on the configured VictoriaMetrics port."
  }
}

run "test_efs_ingress_from_vm_only" {
  command = plan

  assert {
    condition     = aws_security_group_rule.efs_from_vm.from_port == 2049 && aws_security_group_rule.efs_from_vm.type == "ingress"
    error_message = "EFS must only allow NFS ingress on port 2049."
  }
}

run "test_vm_service_is_single_task" {
  command = plan

  assert {
    condition     = aws_ecs_service.vm.desired_count == 1
    error_message = "VictoriaMetrics must run as a single task."
  }
}

run "test_vm_service_stops_before_starting" {
  command = plan

  assert {
    condition     = aws_ecs_service.vm.deployment_minimum_healthy_percent == 0 && aws_ecs_service.vm.deployment_maximum_percent == 100
    error_message = "Deployments must stop the old task before starting the new one to avoid two writers on EFS."
  }
}

run "test_vm_uses_on_demand_fargate_only" {
  command = plan

  assert {
    condition     = length(aws_ecs_cluster_capacity_providers.vm.capacity_providers) == 1 && contains(aws_ecs_cluster_capacity_providers.vm.capacity_providers, "FARGATE")
    error_message = "VictoriaMetrics must use on-demand FARGATE only, never FARGATE_SPOT."
  }
}

run "test_task_uses_arm64" {
  command = plan

  assert {
    condition     = aws_ecs_task_definition.vm.runtime_platform[0].cpu_architecture == "ARM64"
    error_message = "The VictoriaMetrics task must run on ARM64."
  }
}

run "test_container_runs_as_non_root" {
  command = plan

  assert {
    condition     = jsondecode(aws_ecs_task_definition.vm.container_definitions)[0].user == "65532"
    error_message = "The VictoriaMetrics container must run as the non-root user 65532."
  }
}

run "test_access_point_enforces_non_root_owner" {
  command = plan

  assert {
    condition     = aws_efs_access_point.vm.posix_user[0].uid == 65532 && aws_efs_access_point.vm.posix_user[0].gid == 65532
    error_message = "The EFS access point must enforce the non-root POSIX user 65532."
  }
}

run "test_task_mounts_encrypted_efs_volume" {
  command = plan

  assert {
    condition     = one([for v in aws_ecs_task_definition.vm.volume : v if v.name == "vm-data"]).efs_volume_configuration[0].transit_encryption == "ENABLED"
    error_message = "The vm-data volume must enable transit encryption."
  }
}

run "test_log_group_name_and_retention" {
  command = plan

  assert {
    condition     = aws_cloudwatch_log_group.vm.name == "/aws/ecs/${var.project_name}-${var.environment}-observability"
    error_message = "CloudWatch log group name must follow the /aws/ecs/{project}-{environment}-observability format."
  }

  assert {
    condition     = aws_cloudwatch_log_group.vm.retention_in_days == var.log_retention_in_days
    error_message = "CloudWatch log group must use the configured retention."
  }
}

run "test_cluster_name_format" {
  command = plan

  assert {
    condition     = aws_ecs_cluster.vm.name == "${var.project_name}-${var.environment}-observability-cluster"
    error_message = "ECS cluster name must follow the {project}-{environment}-observability-cluster format."
  }
}

run "test_common_tags_applied" {
  command = plan

  assert {
    condition     = alltrue([for k, v in var.common_tags : lookup(aws_efs_file_system.vm.tags, k, null) == v])
    error_message = "common_tags must be applied to the EFS file system."
  }

  assert {
    condition     = alltrue([for k, v in var.common_tags : lookup(aws_ecs_cluster.vm.tags, k, null) == v])
    error_message = "common_tags must be applied to the ECS cluster."
  }
}

run "test_service_discovery_configured" {
  command = plan

  assert {
    condition     = aws_service_discovery_private_dns_namespace.vm.name == "${var.project_name}-${var.environment}-observability.internal"
    error_message = "The service discovery namespace must follow the {project}-{environment}-observability.internal format."
  }

  assert {
    condition     = aws_service_discovery_service.vm.dns_config[0].dns_records[0].type == "A"
    error_message = "The service discovery service must publish an A record."
  }
}
