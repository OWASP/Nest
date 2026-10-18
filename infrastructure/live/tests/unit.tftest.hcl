mock_provider "aws" {
  mock_data "aws_secretsmanager_secret_versions" {
    defaults = {
      versions = [{
        version_id     = "current-version"
        version_stages = ["AWSCURRENT"]
      }]
    }
  }
}

mock_provider "random" {}

variables {
  backend_image_tag      = "test"
  django_configuration   = "Staging"
  django_settings_module = "settings.staging"
  domain_name            = "nest.example.com"
  enable_cron_tasks      = false
  environment            = "staging"
  frontend_image_tag     = "test"
}

run "test_populated_external_secrets_allow_cutover" {
  command = plan

  plan_options {
    target = [data.aws_secretsmanager_secret_versions.external_runtime]
  }

  assert {
    condition     = length(data.aws_secretsmanager_secret_versions.external_runtime) == 7
    error_message = "Validate all seven common external credentials before cutover."
  }
}

run "test_optional_credentials_are_checked" {
  command = plan

  variables {
    enable_additional_parameters = true
    slack_bot_token_suffix       = "CUSTOM_WORKSPACE"
  }

  plan_options {
    target = [data.aws_secretsmanager_secret_versions.external_runtime]
  }

  assert {
    condition = (
      length(data.aws_secretsmanager_secret_versions.external_runtime) == 9 &&
      data.aws_secretsmanager_secret_versions.external_runtime["SLACK_BOT_TOKEN_CUSTOM_WORKSPACE"].secret_id == "/nest/staging/SLACK_BOT_TOKEN_CUSTOM_WORKSPACE"
    )
    error_message = "Validate optional credentials using the configured Slack workspace name."
  }
}

run "test_empty_secret_blocks_cutover_with_ssm_retained" {
  command = plan

  plan_options {
    target = [data.aws_secretsmanager_secret_versions.external_runtime]
  }

  override_data {
    target = data.aws_secretsmanager_secret_versions.external_runtime["GITHUB_TOKEN"]
    values = { versions = [] }
  }

  expect_failures = [data.aws_secretsmanager_secret_versions.external_runtime["GITHUB_TOKEN"]]
}

run "test_previous_version_blocks_cleanup" {
  command = plan

  variables {
    retain_legacy_credential_parameters = false
  }

  plan_options {
    target = [data.aws_secretsmanager_secret_versions.external_runtime]
  }

  override_data {
    target = data.aws_secretsmanager_secret_versions.external_runtime["NEXT_SERVER_GITHUB_CLIENT_SECRET"]
    values = {
      versions = [{
        version_id     = "previous-version"
        version_stages = ["AWSPREVIOUS"]
      }]
    }
  }

  expect_failures = [data.aws_secretsmanager_secret_versions.external_runtime["NEXT_SERVER_GITHUB_CLIENT_SECRET"]]
}

run "test_missing_optional_version_blocks_cutover" {
  command = plan

  variables {
    enable_additional_parameters = true
  }

  plan_options {
    target = [data.aws_secretsmanager_secret_versions.external_runtime]
  }

  override_data {
    target = data.aws_secretsmanager_secret_versions.external_runtime["NEST_GITHUB_APP_PRIVATE_KEY"]
    values = { versions = [] }
  }

  expect_failures = [data.aws_secretsmanager_secret_versions.external_runtime["NEST_GITHUB_APP_PRIVATE_KEY"]]
}
