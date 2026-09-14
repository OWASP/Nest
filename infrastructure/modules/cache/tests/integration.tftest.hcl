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
  common_tags                    = { Environment = "test", Project = "nest" }
  environment                    = "test"
  kms_key_arn                    = "arn:aws:kms:us-east-1:000000000000:key/12345678-1234-1234-1234-123456789012"
  log_retention_in_days          = 30
  project_name                   = "nest"
  redis_engine_version           = "7.0"
  redis_node_type                = "cache.t3.micro"
  redis_num_cache_nodes          = 1
  redis_port                     = 6379
  runtime_secrets_mode           = "prepare"
  secret_recovery_window_in_days = 0
  security_group_ids             = ["sg-12345678"]
  subnet_ids                     = ["subnet-12345678"]
}

run "cache_integration_plan" {
  command = plan

  assert {
    condition     = aws_secretsmanager_secret.django_redis_password.name == "/${var.project_name}/${var.environment}/DJANGO_REDIS_PASSWORD"
    error_message = "Secrets Manager Redis password secret path format is incorrect."
  }

  assert {
    condition     = aws_secretsmanager_secret.django_redis_password.kms_key_id == var.kms_key_arn
    error_message = "Secrets Manager Redis password KMS key ID is incorrect."
  }

  assert {
    condition     = aws_ssm_parameter.django_redis_password[0].name == "/${var.project_name}/${var.environment}/DJANGO_REDIS_PASSWORD"
    error_message = "SSM Redis password parameter name format is incorrect in prepare mode."
  }
}

run "cache_complete_mode_plan" {
  command = plan

  variables {
    runtime_secrets_mode = "complete"
  }

  assert {
    condition     = length(aws_ssm_parameter.django_redis_password) == 0
    error_message = "Complete mode must remove legacy SSM Redis password parameter."
  }
}
