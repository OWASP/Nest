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
  db_allocated_storage           = 20
  db_engine_version              = "16.13"
  db_instance_class              = "db.t3.micro"
  db_name                        = "nest_db"
  db_subnet_ids                  = ["subnet-12345678"]
  db_user                        = "nest_user"
  enable_rds_proxy               = false
  environment                    = "test"
  kms_key_arn                    = "arn:aws:kms:us-east-1:000000000000:key/12345678-1234-1234-1234-123456789012"
  project_name                   = "nest"
  runtime_secrets_mode           = "prepare"
  secret_recovery_window_in_days = 0
  security_group_ids             = ["sg-12345678"]
}

run "database_integration_plan" {
  command = plan

  assert {
    condition     = aws_secretsmanager_secret.db_credentials.kms_key_id == var.kms_key_arn
    error_message = "Database credentials secret KMS key ID is incorrect."
  }

  assert {
    condition     = aws_secretsmanager_secret.db_credentials.name == "${var.project_name}-${var.environment}-db-credentials"
    error_message = "Database credentials secret name format is incorrect."
  }

  assert {
    condition     = aws_ssm_parameter.django_db_password[0].name == "/${var.project_name}/${var.environment}/DJANGO_DB_PASSWORD"
    error_message = "SSM database password parameter name format is incorrect in prepare mode."
  }
}

run "database_complete_mode_plan" {
  command = plan

  variables {
    runtime_secrets_mode = "complete"
  }

  assert {
    condition     = length(aws_ssm_parameter.django_db_password) == 0
    error_message = "Complete mode must remove legacy SSM database password parameter."
  }
}
