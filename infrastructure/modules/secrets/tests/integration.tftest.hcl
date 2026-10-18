provider "aws" {
  access_key                  = "test"
  region                      = "us-east-1"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
}

variables {
  common_tags                    = { Environment = "test", Project = "nest" }
  django_secret_key              = "existing-django-secret-key"
  environment                    = "test"
  kms_key_arn                    = "arn:aws:kms:us-east-1:000000000000:key/12345678-1234-1234-1234-123456789012"
  nextauth_secret                = "existing-nextauth-secret"
  project_name                   = "nest"
  secret_recovery_window_in_days = 0
  slack_bot_token_suffix         = "T04T40NHX"
}

run "secrets_integration_apply" {
  command = apply

  assert {
    condition = (
      aws_secretsmanager_secret_version.django_secret_key.secret_string == var.django_secret_key &&
      aws_secretsmanager_secret_version.nextauth_secret.secret_string == var.nextauth_secret &&
      contains(aws_secretsmanager_secret_version.django_secret_key.version_stages, "AWSCURRENT") &&
      contains(aws_secretsmanager_secret_version.nextauth_secret.version_stages, "AWSCURRENT")
    )
    error_message = "Generated credential versions must contain the supplied values and be marked AWSCURRENT."
  }

  assert {
    condition = (
      length(aws_secretsmanager_secret.external_runtime) == 7 &&
      aws_secretsmanager_secret.external_runtime["GITHUB_TOKEN"].name == "/${var.project_name}/${var.environment}/GITHUB_TOKEN"
    )
    error_message = "External secret containers must use the existing environment namespace."
  }
}

run "secrets_integration_additional" {
  command = apply

  variables {
    enable_additional_secrets = true
  }

  assert {
    condition = (
      length(aws_secretsmanager_secret.external_runtime) == 9 &&
      aws_secretsmanager_secret.external_runtime["NEST_GITHUB_APP_PRIVATE_KEY"].name == "/${var.project_name}/${var.environment}/NEST_GITHUB_APP_PRIVATE_KEY" &&
      aws_secretsmanager_secret.external_runtime["SLACK_BOT_TOKEN_${var.slack_bot_token_suffix}"].name == "/${var.project_name}/${var.environment}/SLACK_BOT_TOKEN_${var.slack_bot_token_suffix}"
    )
    error_message = "Optional secret containers must retain their existing GitHub App and Slack names."
  }
}
