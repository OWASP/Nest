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
  common_tags                   = { Environment = "test", Project = "nest" }
  django_allowed_hosts          = "nest.owasp.dev"
  django_allowed_origins        = "https://nest.owasp.dev"
  django_aws_static_bucket_name = "nest-test-static-abcd1234"
  django_configuration          = "Staging"
  django_db_host                = "db.example.com"
  django_db_name                = "nest_db"
  django_db_port                = "5432"
  django_db_user                = "nest_user"
  django_redis_host             = "redis.example.com"
  django_release_version        = "1.0.0"
  django_settings_module        = "settings.staging"
  enable_additional_parameters  = true
  environment                   = "test"
  next_server_csrf_url          = "https://nest.owasp.dev/csrf"
  next_server_graphql_url       = "https://nest.owasp.dev/graphql"
  nextauth_url                  = "https://nest.owasp.dev"
  project_name                  = "nest"
  slack_bot_token_suffix        = "T04T40NHX"
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
    condition     = aws_ssm_parameter.django_secret_key[0].name == "/${var.project_name}/${var.environment}/DJANGO_SECRET_KEY"
    error_message = "SSM django_secret_key parameter path format is incorrect."
  }

  assert {
    condition     = aws_ssm_parameter.django_secret_key[0].type == "SecureString"
    error_message = "SSM django_secret_key parameter type must be SecureString."
  }

}

run "parameters_integration_cleanup" {
  command = apply

  variables {
    enable_additional_parameters        = true
    retain_legacy_credential_parameters = false
  }

  assert {
    condition = (
      length(aws_ssm_parameter.django_algolia_write_api_key) == 0 &&
      length(aws_ssm_parameter.django_open_ai_secret_key) == 0 &&
      length(aws_ssm_parameter.django_secret_key) == 0 &&
      length(aws_ssm_parameter.django_sentry_dsn) == 0 &&
      length(aws_ssm_parameter.django_slack_bot_token) == 0 &&
      length(aws_ssm_parameter.django_slack_signing_secret) == 0 &&
      length(aws_ssm_parameter.github_token) == 0 &&
      length(aws_ssm_parameter.next_server_github_client_secret) == 0 &&
      length(aws_ssm_parameter.nextauth_secret) == 0 &&
      length(aws_ssm_parameter.nest_github_app_private_key) == 0 &&
      length(aws_ssm_parameter.slack_bot_token) == 0
    )
    error_message = "Explicit cleanup must remove all common and optional migrated SSM credentials."
  }

  assert {
    condition = (
      aws_ssm_parameter.django_algolia_application_id.type == "SecureString" &&
      output.django_ssm_parameter_arns["DJANGO_ALGOLIA_APPLICATION_ID"] == aws_ssm_parameter.django_algolia_application_id.arn &&
      output.django_ssm_parameter_arns["DJANGO_ALLOWED_HOSTS"] == aws_ssm_parameter.django_allowed_hosts.arn &&
      output.django_ssm_parameter_arns["DJANGO_GITHUB_APP_ID"] == aws_ssm_parameter.django_github_app_id[0].arn &&
      output.frontend_ssm_parameter_arns["NEXT_SERVER_GITHUB_CLIENT_ID"] == aws_ssm_parameter.next_server_github_client_id.arn &&
      output.django_secret_key == random_string.django_secret_key.result &&
      output.nextauth_secret == random_string.nextauth_secret.result
    )
    error_message = "Cleanup must retain configuration parameters and the generated values used by the secrets module."
  }
}

run "parameters_integration_after_cleanup" {
  command = plan

  variables {
    retain_legacy_credential_parameters = false
  }

  assert {
    condition = (
      output.django_ssm_parameter_arns == run.parameters_integration_apply.django_ssm_parameter_arns &&
      output.frontend_ssm_parameter_arns == run.parameters_integration_apply.frontend_ssm_parameter_arns &&
      length(aws_ssm_parameter.django_secret_key) == 0 &&
      length(aws_ssm_parameter.nextauth_secret) == 0 &&
      length(aws_ssm_parameter.slack_bot_token) == 0
    )
    error_message = "Later deployments with cleanup persisted must keep runtime references and must not recreate legacy credentials."
  }
}
