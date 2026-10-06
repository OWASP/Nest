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
  db_password_arn                = "arn:aws:ssm:us-east-1:000000000000:parameter/nest/test/DJANGO_DB_PASSWORD"
  django_allowed_hosts           = "nest.owasp.dev"
  django_allowed_origins         = "https://nest.owasp.dev"
  django_aws_static_bucket_name  = "nest-test-static-abcd1234"
  django_configuration           = "Staging"
  django_db_host                 = "db.example.com"
  django_db_name                 = "nest_db"
  django_db_port                 = "5432"
  django_db_user                 = "nest_user"
  django_redis_host              = "redis.example.com"
  django_release_version         = "1.0.0"
  django_settings_module         = "settings.staging"
  environment                    = "test"
  kms_key_arn                    = "arn:aws:kms:us-east-1:000000000000:key/12345678-1234-1234-1234-123456789012"
  next_server_csrf_url           = "https://nest.owasp.dev/csrf"
  next_server_graphql_url        = "https://nest.owasp.dev/graphql"
  nextauth_url                   = "https://nest.owasp.dev"
  project_name                   = "nest"
  redis_password_arn             = "arn:aws:ssm:us-east-1:000000000000:parameter/nest/test/DJANGO_REDIS_PASSWORD"
  secret_recovery_window_in_days = 0
  slack_bot_token_suffix         = "T04T40NHX"
}

run "parameters_integration_apply" {
  command = apply

  assert {
    condition     = aws_ssm_parameter.django_allowed_hosts.name == "/${var.project_name}/${var.environment}/DJANGO_ALLOWED_HOSTS"
    error_message = "SSM parameter path format is incorrect."
  }

  assert {
    condition     = aws_ssm_parameter.django_allowed_hosts.value == var.django_allowed_hosts
    error_message = "SSM parameter value format is incorrect."
  }

  assert {
    condition     = aws_ssm_parameter.django_db_host.name == "/${var.project_name}/${var.environment}/DJANGO_DB_HOST"
    error_message = "SSM database host parameter path format is incorrect."
  }

  assert {
    condition     = aws_ssm_parameter.django_db_host.value == var.django_db_host
    error_message = "SSM database host parameter value format is incorrect."
  }

  assert {
    condition     = aws_ssm_parameter.nextauth_url.name == "/${var.project_name}/${var.environment}/NEXTAUTH_URL"
    error_message = "SSM nextauth_url parameter path format is incorrect."
  }

  assert {
    condition     = aws_ssm_parameter.nextauth_url.value == var.nextauth_url
    error_message = "SSM nextauth_url parameter value format is incorrect."
  }

  assert {
    condition     = aws_ssm_parameter.django_secret_key.name == "/${var.project_name}/${var.environment}/DJANGO_SECRET_KEY"
    error_message = "SSM django_secret_key parameter path format is incorrect."
  }

  assert {
    condition     = aws_ssm_parameter.django_secret_key.type == "SecureString"
    error_message = "SSM django_secret_key parameter type must be SecureString."
  }

  assert {
    condition = (
      aws_secretsmanager_secret_version.django_secret_key.secret_string == aws_ssm_parameter.django_secret_key.value &&
      aws_secretsmanager_secret_version.nextauth_secret.secret_string == aws_ssm_parameter.nextauth_secret.value
    )
    error_message = "Secrets Manager must receive the existing Django and NextAuth values while SSM is retained."
  }

  assert {
    condition     = aws_secretsmanager_secret.external_runtime["GITHUB_TOKEN"].name == "/${var.project_name}/${var.environment}/GITHUB_TOKEN"
    error_message = "External runtime secrets must be provisioned in the existing environment namespace."
  }
}
