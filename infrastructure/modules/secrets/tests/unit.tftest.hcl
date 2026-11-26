mock_provider "aws" {}

variables {
  common_tags            = { Environment = "test", Project = "nest" }
  django_secret_key      = "existing-django-secret-key"
  environment            = "test"
  kms_key_arn            = "arn:aws:kms:us-east-2:123456789012:key/12345678-1234-1234-1234-123456789012"
  nextauth_secret        = "existing-nextauth-secret"
  project_name           = "nest"
  slack_bot_token_suffix = "T04T40NHX"
}

run "test_runtime_secret_inventory" {
  command = plan

  variables {
    secret_recovery_window_in_days = 30
  }

  assert {
    condition = toset(keys(aws_secretsmanager_secret.external_runtime)) == toset([
      "DJANGO_ALGOLIA_WRITE_API_KEY",
      "DJANGO_OPEN_AI_SECRET_KEY",
      "DJANGO_SENTRY_DSN",
      "DJANGO_SLACK_BOT_TOKEN",
      "DJANGO_SLACK_SIGNING_SECRET",
      "GITHUB_TOKEN",
      "NEXT_SERVER_GITHUB_CLIENT_SECRET",
    ])
    error_message = "Provision the external runtime secrets without production-only credentials."
  }

  assert {
    condition = alltrue([
      for name, secret in aws_secretsmanager_secret.external_runtime :
      secret.name == "/${var.project_name}/${var.environment}/${name}" &&
      secret.kms_key_id == var.kms_key_arn &&
      secret.recovery_window_in_days == var.secret_recovery_window_in_days &&
      secret.tags == var.common_tags
      ]) && alltrue([
      for secret in [aws_secretsmanager_secret.django_secret_key, aws_secretsmanager_secret.nextauth_secret] :
      secret.kms_key_id == var.kms_key_arn &&
      secret.recovery_window_in_days == var.secret_recovery_window_in_days &&
      secret.tags == var.common_tags
    ])
    error_message = "Runtime secrets must use the environment namespace, configured KMS key, recovery window, and tags."
  }

  assert {
    condition = (
      aws_secretsmanager_secret.django_secret_key.name == "/${var.project_name}/${var.environment}/DJANGO_SECRET_KEY" &&
      aws_secretsmanager_secret.nextauth_secret.name == "/${var.project_name}/${var.environment}/NEXTAUTH_SECRET"
    )
    error_message = "Generated credential secrets must keep their existing names."
  }
}

run "test_generated_secrets_preserve_supplied_values" {
  command = apply

  assert {
    condition = (
      aws_secretsmanager_secret_version.django_secret_key.secret_string == var.django_secret_key &&
      aws_secretsmanager_secret_version.nextauth_secret.secret_string == var.nextauth_secret
    )
    error_message = "Secrets Manager must store the supplied Django and NextAuth credentials without generating replacements."
  }
}

run "test_additional_runtime_secret_names" {
  command = plan

  variables {
    enable_additional_secrets = true
    slack_bot_token_suffix    = "CUSTOM_WORKSPACE"
  }

  assert {
    condition = (
      length(aws_secretsmanager_secret.external_runtime) == 9 &&
      aws_secretsmanager_secret.external_runtime["NEST_GITHUB_APP_PRIVATE_KEY"].name == "/${var.project_name}/${var.environment}/NEST_GITHUB_APP_PRIVATE_KEY" &&
      aws_secretsmanager_secret.external_runtime["SLACK_BOT_TOKEN_CUSTOM_WORKSPACE"].name == "/${var.project_name}/${var.environment}/SLACK_BOT_TOKEN_CUSTOM_WORKSPACE"
    )
    error_message = "Additional secrets must preserve the GitHub App name and configured Slack workspace suffix."
  }
}

run "test_invalid_recovery_window" {
  command = plan

  variables {
    secret_recovery_window_in_days = 1
  }

  expect_failures = [var.secret_recovery_window_in_days]
}

run "test_fractional_recovery_window_is_rejected" {
  command = plan

  variables {
    secret_recovery_window_in_days = 7.5
  }

  expect_failures = [var.secret_recovery_window_in_days]
}
