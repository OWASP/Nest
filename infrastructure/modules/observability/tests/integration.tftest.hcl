provider "aws" {
  access_key                  = "test"
  region                      = "us-east-1"
  s3_use_path_style           = true
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
}

variables {
  aws_region   = "us-east-1"
  common_tags  = { Environment = "test", Project = "nest" }
  environment  = "test"
  project_name = "nest"
  vm_image     = "victoriametrics/victoria-metrics:v1.145.0@sha256:c014fb5a711d38cb24fd0673197592cd1394bb903dbb16aea565620c9c8a3d70"
}

run "setup" {
  module {
    source = "./tests/setup"
  }
}

run "observability_integration_apply" {
  command = apply

  variables {
    app_security_group_ids = run.setup.app_security_group_ids
    kms_key_arn            = run.setup.kms_key_arn
    subnet_ids             = run.setup.subnet_ids
    vm_desired_count       = 0
    vpc_id                 = run.setup.vpc_id
  }

  assert {
    condition     = can(aws_efs_file_system.vm.id)
    error_message = "EFS file system was not created."
  }

  assert {
    condition     = aws_efs_file_system.vm.encrypted == true
    error_message = "EFS must be encrypted at rest."
  }

  assert {
    condition     = length(aws_efs_mount_target.vm) == length(var.subnet_ids)
    error_message = "There must be one EFS mount target per subnet."
  }

  assert {
    condition     = aws_security_group_rule.efs_from_vm.source_security_group_id == aws_security_group.vm.id
    error_message = "EFS ingress must come only from the VictoriaMetrics security group."
  }

  assert {
    condition     = one([for v in aws_ecs_task_definition.vm.volume : v if v.name == "vm-data"]).efs_volume_configuration[0].file_system_id == aws_efs_file_system.vm.id
    error_message = "The vm-data volume must reference the module's EFS file system."
  }

  assert {
    condition     = can(aws_efs_access_point.vm.id)
    error_message = "EFS access point was not created."
  }

  assert {
    condition     = one([for v in aws_ecs_task_definition.vm.volume : v if v.name == "vm-data"]).efs_volume_configuration[0].authorization_config[0].access_point_id == aws_efs_access_point.vm.id
    error_message = "The vm-data volume must mount through the EFS access point (for non-root UID enforcement)."
  }

  assert {
    condition     = can(aws_ecs_service.vm.id)
    error_message = "ECS service was not created."
  }
}
