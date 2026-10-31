mock_provider "aws" {
  mock_data "aws_secretsmanager_secret_version" {
    defaults = {
      secret_string = "working-credential"
    }
  }
}

mock_provider "random" {}

override_module {
  target = module.parameters

  outputs = {
    django_secret_key           = "existing-django-secret-key"
    nextauth_secret             = "existing-nextauth-secret"
    django_ssm_parameter_arns   = {}
    frontend_ssm_parameter_arns = {}
    external_secret_values = {
      DJANGO_ALGOLIA_WRITE_API_KEY     = "working-credential"
      DJANGO_OPEN_AI_SECRET_KEY        = "working-credential"
      DJANGO_SENTRY_DSN                = "working-credential"
      DJANGO_SLACK_BOT_TOKEN           = "working-credential"
      DJANGO_SLACK_SIGNING_SECRET      = "working-credential"
      GITHUB_TOKEN                     = "working-credential"
      NEXT_SERVER_GITHUB_CLIENT_SECRET = "working-credential"
      NEST_GITHUB_APP_PRIVATE_KEY      = "working-credential"
      SLACK_BOT_TOKEN_T04T40NHX        = "working-credential"
      SLACK_BOT_TOKEN_CUSTOM_WORKSPACE = "working-credential"
    }
  }
}

variables {
  backend_image_tag      = "test"
  django_configuration   = "Staging"
  django_settings_module = "settings.staging"
  domain_name            = "nest.example.com"
  enable_cron_tasks      = false
  environment            = "staging"
  frontend_image_tag     = "test"
}

run "test_matching_external_credentials_allow_cutover" {
  command = plan

  plan_options {
    target = [data.aws_secretsmanager_secret_version.external_runtime]
  }

  assert {
    condition     = length(data.aws_secretsmanager_secret_version.external_runtime) == 7
    error_message = "Validate all seven common AWSCURRENT credentials before cutover."
  }
}

run "test_optional_credentials_use_configured_slack_suffix" {
  command = plan

  variables {
    enable_additional_parameters = true
    slack_bot_token_suffix       = "CUSTOM_WORKSPACE"
  }

  plan_options {
    target = [data.aws_secretsmanager_secret_version.external_runtime]
  }

  assert {
    condition = (
      length(data.aws_secretsmanager_secret_version.external_runtime) == 9 &&
      data.aws_secretsmanager_secret_version.external_runtime["SLACK_BOT_TOKEN_CUSTOM_WORKSPACE"].secret_id == "/nest/staging/SLACK_BOT_TOKEN_CUSTOM_WORKSPACE"
    )
    error_message = "Validate both optional credentials using the configured Slack workspace name."
  }
}

run "test_empty_credential_blocks_cutover" {
  command = plan

  plan_options {
    target = [data.aws_secretsmanager_secret_version.external_runtime]
  }

  override_data {
    target = data.aws_secretsmanager_secret_version.external_runtime["GITHUB_TOKEN"]
    values = { secret_string = "" }
  }

  expect_failures = [data.aws_secretsmanager_secret_version.external_runtime["GITHUB_TOKEN"]]
}

run "test_placeholder_credential_blocks_cutover" {
  command = plan

  plan_options {
    target = [data.aws_secretsmanager_secret_version.external_runtime]
  }

  override_data {
    target = data.aws_secretsmanager_secret_version.external_runtime["GITHUB_TOKEN"]
    values = { secret_string = "to-be-set-in-aws-console" }
  }

  expect_failures = [data.aws_secretsmanager_secret_version.external_runtime["GITHUB_TOKEN"]]
}

run "test_whitespace_credential_blocks_cutover" {
  command = plan

  plan_options {
    target = [data.aws_secretsmanager_secret_version.external_runtime]
  }

  override_data {
    target = data.aws_secretsmanager_secret_version.external_runtime["GITHUB_TOKEN"]
    values = { secret_string = "   " }
  }

  expect_failures = [data.aws_secretsmanager_secret_version.external_runtime["GITHUB_TOKEN"]]
}

run "test_mismatched_credential_blocks_cutover" {
  command = plan

  plan_options {
    target = [data.aws_secretsmanager_secret_version.external_runtime]
  }

  override_data {
    target = data.aws_secretsmanager_secret_version.external_runtime["GITHUB_TOKEN"]
    values = { secret_string = "different-working-credential" }
  }

  expect_failures = [data.aws_secretsmanager_secret_version.external_runtime["GITHUB_TOKEN"]]
}

run "test_optional_mismatch_blocks_cutover" {
  command = plan

  variables {
    enable_additional_parameters = true
    slack_bot_token_suffix       = "CUSTOM_WORKSPACE"
  }

  plan_options {
    target = [data.aws_secretsmanager_secret_version.external_runtime]
  }

  override_data {
    target = data.aws_secretsmanager_secret_version.external_runtime["SLACK_BOT_TOKEN_CUSTOM_WORKSPACE"]
    values = { secret_string = "different-workspace-credential" }
  }

  expect_failures = [data.aws_secretsmanager_secret_version.external_runtime["SLACK_BOT_TOKEN_CUSTOM_WORKSPACE"]]
}

run "test_cleanup_does_not_read_removed_ssm_values" {
  command = plan

  variables {
    retain_legacy_credential_parameters = false
  }

  plan_options {
    target = [data.aws_secretsmanager_secret_version.external_runtime]
  }

  override_module {
    target = module.parameters

    outputs = {
      django_secret_key           = "existing-django-secret-key"
      nextauth_secret             = "existing-nextauth-secret"
      django_ssm_parameter_arns   = {}
      frontend_ssm_parameter_arns = {}
      external_secret_values      = {}
    }
  }

  override_data {
    target = data.aws_secretsmanager_secret_version.external_runtime["GITHUB_TOKEN"]
    values = { secret_string = "updated-directly-in-secrets-manager" }
  }

  assert {
    condition     = data.aws_secretsmanager_secret_version.external_runtime["GITHUB_TOKEN"].secret_string == "updated-directly-in-secrets-manager"
    error_message = "After ownership handoff, valid Secrets Manager credentials must work without legacy SSM values."
  }
}

run "test_placeholder_blocks_cleanup" {
  command = plan

  variables {
    retain_legacy_credential_parameters = false
  }

  plan_options {
    target = [data.aws_secretsmanager_secret_version.external_runtime]
  }

  override_module {
    target = module.parameters

    outputs = {
      django_secret_key           = "existing-django-secret-key"
      nextauth_secret             = "existing-nextauth-secret"
      django_ssm_parameter_arns   = {}
      frontend_ssm_parameter_arns = {}
      external_secret_values      = {}
    }
  }

  override_data {
    target = data.aws_secretsmanager_secret_version.external_runtime["GITHUB_TOKEN"]
    values = { secret_string = "to-be-set-in-aws-console" }
  }

  expect_failures = [data.aws_secretsmanager_secret_version.external_runtime["GITHUB_TOKEN"]]
}
