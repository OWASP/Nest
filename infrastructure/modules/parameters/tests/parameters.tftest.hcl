mock_provider "aws" {}

variables {
  common_tags                   = { Environment = "test", Project = "nest" }
  db_password_arn               = "arn:aws:ssm:us-east-2:123456789012:parameter/nest/test/DJANGO_DB_PASSWORD"
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
  environment                   = "test"
  next_server_csrf_url          = "https://nest.owasp.dev/csrf"
  next_server_graphql_url       = "https://nest.owasp.dev/graphql"
  nextauth_url                  = "https://nest.owasp.dev"
  project_name                  = "nest"
  redis_password_arn            = "arn:aws:ssm:us-east-2:123456789012:parameter/nest/test/DJANGO_REDIS_PASSWORD"
  slack_bot_token_suffix        = "T04T40NHX"
}

run "test_django_algolia_application_id_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_algolia_application_id.name == "/${var.project_name}/${var.environment}/DJANGO_ALGOLIA_APPLICATION_ID"
    error_message = "DJANGO_ALGOLIA_APPLICATION_ID must follow path: /{project}/{environment}/DJANGO_ALGOLIA_APPLICATION_ID."
  }
}

run "test_django_algolia_application_id_is_secure_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_algolia_application_id.type == "SecureString"
    error_message = "DJANGO_ALGOLIA_APPLICATION_ID must be stored as SecureString."
  }
}

run "test_django_algolia_write_api_key_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_algolia_write_api_key.name == "/${var.project_name}/${var.environment}/DJANGO_ALGOLIA_WRITE_API_KEY"
    error_message = "DJANGO_ALGOLIA_WRITE_API_KEY must follow path: /{project}/{environment}/DJANGO_ALGOLIA_WRITE_API_KEY."
  }
}

run "test_django_algolia_write_api_key_is_secure_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_algolia_write_api_key.type == "SecureString"
    error_message = "DJANGO_ALGOLIA_WRITE_API_KEY must be stored as SecureString."
  }
}

run "test_django_allowed_hosts_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_allowed_hosts.name == "/${var.project_name}/${var.environment}/DJANGO_ALLOWED_HOSTS"
    error_message = "DJANGO_ALLOWED_HOSTS must follow path: /{project}/{environment}/DJANGO_ALLOWED_HOSTS."
  }
}

run "test_django_allowed_hosts_is_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_allowed_hosts.type == "String"
    error_message = "DJANGO_ALLOWED_HOSTS must be stored as String."
  }
}

run "test_django_allowed_origins_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_allowed_origins.name == "/${var.project_name}/${var.environment}/DJANGO_ALLOWED_ORIGINS"
    error_message = "DJANGO_ALLOWED_ORIGINS must follow path: /{project}/{environment}/DJANGO_ALLOWED_ORIGINS."
  }
}

run "test_django_allowed_origins_is_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_allowed_origins.type == "String"
    error_message = "DJANGO_ALLOWED_ORIGINS must be stored as String."
  }
}

run "test_django_aws_storage_bucket_name_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_aws_storage_bucket_name.name == "/${var.project_name}/${var.environment}/DJANGO_AWS_STORAGE_BUCKET_NAME"
    error_message = "DJANGO_AWS_STORAGE_BUCKET_NAME must follow path: /{project}/{environment}/DJANGO_AWS_STORAGE_BUCKET_NAME."
  }
}

run "test_django_aws_storage_bucket_name_is_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_aws_storage_bucket_name.type == "String"
    error_message = "DJANGO_AWS_STORAGE_BUCKET_NAME must be stored as String."
  }
}

run "test_django_configuration_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_configuration.name == "/${var.project_name}/${var.environment}/DJANGO_CONFIGURATION"
    error_message = "DJANGO_CONFIGURATION must follow path: /{project}/{environment}/DJANGO_CONFIGURATION."
  }
}

run "test_django_configuration_is_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_configuration.type == "String"
    error_message = "DJANGO_CONFIGURATION must be stored as String."
  }
}

run "test_django_db_host_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_db_host.name == "/${var.project_name}/${var.environment}/DJANGO_DB_HOST"
    error_message = "DJANGO_DB_HOST must follow path: /{project}/{environment}/DJANGO_DB_HOST."
  }
}

run "test_django_db_host_is_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_db_host.type == "String"
    error_message = "DJANGO_DB_HOST must be stored as String."
  }
}

run "test_django_db_name_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_db_name.name == "/${var.project_name}/${var.environment}/DJANGO_DB_NAME"
    error_message = "DJANGO_DB_NAME must follow path: /{project}/{environment}/DJANGO_DB_NAME."
  }
}

run "test_django_db_name_is_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_db_name.type == "String"
    error_message = "DJANGO_DB_NAME must be stored as String."
  }
}

run "test_django_db_port_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_db_port.name == "/${var.project_name}/${var.environment}/DJANGO_DB_PORT"
    error_message = "DJANGO_DB_PORT must follow path: /{project}/{environment}/DJANGO_DB_PORT."
  }
}

run "test_django_db_port_is_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_db_port.type == "String"
    error_message = "DJANGO_DB_PORT must be stored as String."
  }
}

run "test_django_db_user_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_db_user.name == "/${var.project_name}/${var.environment}/DJANGO_DB_USER"
    error_message = "DJANGO_DB_USER must follow path: /{project}/{environment}/DJANGO_DB_USER."
  }
}

run "test_django_db_user_is_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_db_user.type == "String"
    error_message = "DJANGO_DB_USER must be stored as String."
  }
}

run "test_django_github_app_id_disabled_by_default" {
  command = plan
  assert {
    condition     = length(aws_ssm_parameter.django_github_app_id) == 0
    error_message = "DJANGO_GITHUB_APP_ID must not be created when enable_additional_parameters is false."
  }
}

run "test_django_github_app_id_is_string" {
  command = plan
  variables {
    enable_additional_parameters = true
  }
  assert {
    condition     = aws_ssm_parameter.django_github_app_id[0].type == "String"
    error_message = "DJANGO_GITHUB_APP_ID must be stored as String."
  }
}

run "test_django_github_app_id_path_format" {
  command = plan
  variables {
    enable_additional_parameters = true
  }
  assert {
    condition     = aws_ssm_parameter.django_github_app_id[0].name == "/${var.project_name}/${var.environment}/DJANGO_GITHUB_APP_ID"
    error_message = "DJANGO_GITHUB_APP_ID must follow path: /{project}/{environment}/DJANGO_GITHUB_APP_ID."
  }
}

run "test_django_github_app_installation_id_disabled_by_default" {
  command = plan
  assert {
    condition     = length(aws_ssm_parameter.django_github_app_installation_id) == 0
    error_message = "DJANGO_GITHUB_APP_INSTALLATION_ID must not be created when enable_additional_parameters is false."
  }
}

run "test_django_github_app_installation_id_is_string" {
  command = plan
  variables {
    enable_additional_parameters = true
  }
  assert {
    condition     = aws_ssm_parameter.django_github_app_installation_id[0].type == "String"
    error_message = "DJANGO_GITHUB_APP_INSTALLATION_ID must be stored as String."
  }
}

run "test_django_github_app_installation_id_path_format" {
  command = plan
  variables {
    enable_additional_parameters = true
  }
  assert {
    condition     = aws_ssm_parameter.django_github_app_installation_id[0].name == "/${var.project_name}/${var.environment}/DJANGO_GITHUB_APP_INSTALLATION_ID"
    error_message = "DJANGO_GITHUB_APP_INSTALLATION_ID must follow path: /{project}/{environment}/DJANGO_GITHUB_APP_INSTALLATION_ID."
  }
}

run "test_django_open_ai_secret_key_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_open_ai_secret_key.name == "/${var.project_name}/${var.environment}/DJANGO_OPEN_AI_SECRET_KEY"
    error_message = "DJANGO_OPEN_AI_SECRET_KEY must follow path: /{project}/{environment}/DJANGO_OPEN_AI_SECRET_KEY."
  }
}

run "test_django_open_ai_secret_key_is_secure_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_open_ai_secret_key.type == "SecureString"
    error_message = "DJANGO_OPEN_AI_SECRET_KEY must be stored as SecureString."
  }
}

run "test_django_redis_host_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_redis_host.name == "/${var.project_name}/${var.environment}/DJANGO_REDIS_HOST"
    error_message = "DJANGO_REDIS_HOST must follow path: /{project}/{environment}/DJANGO_REDIS_HOST."
  }
}

run "test_django_redis_host_is_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_redis_host.type == "String"
    error_message = "DJANGO_REDIS_HOST must be stored as String."
  }
}

run "test_django_redis_use_tls_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_redis_use_tls.name == "/${var.project_name}/${var.environment}/DJANGO_REDIS_USE_TLS"
    error_message = "DJANGO_REDIS_USE_TLS must follow path: /{project}/{environment}/DJANGO_REDIS_USE_TLS."
  }
}

run "test_django_redis_use_tls_is_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_redis_use_tls.type == "String"
    error_message = "DJANGO_REDIS_USE_TLS must be stored as String."
  }
}

run "test_django_release_version_is_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_release_version.type == "String"
    error_message = "DJANGO_RELEASE_VERSION must be stored as String."
  }
}

run "test_django_release_version_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_release_version.name == "/${var.project_name}/${var.environment}/DJANGO_RELEASE_VERSION"
    error_message = "DJANGO_RELEASE_VERSION must follow path: /{project}/{environment}/DJANGO_RELEASE_VERSION."
  }
}

run "test_django_secret_key_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_secret_key.name == "/${var.project_name}/${var.environment}/DJANGO_SECRET_KEY"
    error_message = "DJANGO_SECRET_KEY must follow path: /{project}/{environment}/DJANGO_SECRET_KEY."
  }
}

run "test_django_secret_key_is_secure_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_secret_key.type == "SecureString"
    error_message = "DJANGO_SECRET_KEY must be stored as SecureString."
  }
}

run "test_django_settings_module_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_settings_module.name == "/${var.project_name}/${var.environment}/DJANGO_SETTINGS_MODULE"
    error_message = "DJANGO_SETTINGS_MODULE must follow path: /{project}/{environment}/DJANGO_SETTINGS_MODULE."
  }
}

run "test_django_settings_module_is_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_settings_module.type == "String"
    error_message = "DJANGO_SETTINGS_MODULE must be stored as String."
  }
}

run "test_django_sentry_dsn_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_sentry_dsn.name == "/${var.project_name}/${var.environment}/DJANGO_SENTRY_DSN"
    error_message = "DJANGO_SENTRY_DSN must follow path: /{project}/{environment}/DJANGO_SENTRY_DSN."
  }
}

run "test_django_sentry_dsn_is_secure_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_sentry_dsn.type == "SecureString"
    error_message = "DJANGO_SENTRY_DSN must be stored as SecureString."
  }
}

run "test_django_slack_bot_token_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_slack_bot_token.name == "/${var.project_name}/${var.environment}/DJANGO_SLACK_BOT_TOKEN"
    error_message = "DJANGO_SLACK_BOT_TOKEN must follow path: /{project}/{environment}/DJANGO_SLACK_BOT_TOKEN."
  }
}

run "test_django_slack_bot_token_is_secure_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_slack_bot_token.type == "SecureString"
    error_message = "DJANGO_SLACK_BOT_TOKEN must be stored as SecureString."
  }
}

run "test_django_slack_signing_secret_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_slack_signing_secret.name == "/${var.project_name}/${var.environment}/DJANGO_SLACK_SIGNING_SECRET"
    error_message = "DJANGO_SLACK_SIGNING_SECRET must follow path: /{project}/{environment}/DJANGO_SLACK_SIGNING_SECRET."
  }
}

run "test_django_slack_signing_secret_is_secure_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.django_slack_signing_secret.type == "SecureString"
    error_message = "DJANGO_SLACK_SIGNING_SECRET must be stored as SecureString."
  }
}

run "test_github_token_is_secure_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.github_token.type == "SecureString"
    error_message = "GITHUB_TOKEN must be stored as SecureString."
  }
}

run "test_github_token_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.github_token.name == "/${var.project_name}/${var.environment}/GITHUB_TOKEN"
    error_message = "GITHUB_TOKEN must follow path: /{project}/{environment}/GITHUB_TOKEN."
  }
}

run "test_nest_github_app_private_key_disabled_by_default" {
  command = plan
  assert {
    condition     = length(aws_ssm_parameter.nest_github_app_private_key) == 0
    error_message = "NEST_GITHUB_APP_PRIVATE_KEY must not be created when enable_additional_parameters is false."
  }
}

run "test_nest_github_app_private_key_is_secure_string" {
  command = plan
  variables {
    enable_additional_parameters = true
  }
  assert {
    condition     = aws_ssm_parameter.nest_github_app_private_key[0].type == "SecureString"
    error_message = "NEST_GITHUB_APP_PRIVATE_KEY must be stored as SecureString."
  }
}

run "test_nest_github_app_private_key_path_format" {
  command = plan
  variables {
    enable_additional_parameters = true
  }
  assert {
    condition     = aws_ssm_parameter.nest_github_app_private_key[0].name == "/${var.project_name}/${var.environment}/NEST_GITHUB_APP_PRIVATE_KEY"
    error_message = "NEST_GITHUB_APP_PRIVATE_KEY must follow path: /{project}/{environment}/NEST_GITHUB_APP_PRIVATE_KEY."
  }
}

run "test_next_server_csrf_url_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.next_server_csrf_url.name == "/${var.project_name}/${var.environment}/NEXT_SERVER_CSRF_URL"
    error_message = "NEXT_SERVER_CSRF_URL must follow path: /{project}/{environment}/NEXT_SERVER_CSRF_URL."
  }
}

run "test_next_server_csrf_url_is_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.next_server_csrf_url.type == "String"
    error_message = "NEXT_SERVER_CSRF_URL must be stored as String."
  }
}

run "test_next_server_disable_ssr_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.next_server_disable_ssr.name == "/${var.project_name}/${var.environment}/NEXT_SERVER_DISABLE_SSR"
    error_message = "NEXT_SERVER_DISABLE_SSR must follow path: /{project}/{environment}/NEXT_SERVER_DISABLE_SSR."
  }
}

run "test_next_server_disable_ssr_is_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.next_server_disable_ssr.type == "String"
    error_message = "NEXT_SERVER_DISABLE_SSR must be stored as String."
  }
}

run "test_next_server_github_client_id_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.next_server_github_client_id.name == "/${var.project_name}/${var.environment}/NEXT_SERVER_GITHUB_CLIENT_ID"
    error_message = "NEXT_SERVER_GITHUB_CLIENT_ID must follow path: /{project}/{environment}/NEXT_SERVER_GITHUB_CLIENT_ID."
  }
}

run "test_next_server_github_client_id_is_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.next_server_github_client_id.type == "String"
    error_message = "NEXT_SERVER_GITHUB_CLIENT_ID must be stored as String."
  }
}

run "test_next_server_github_client_secret_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.next_server_github_client_secret.name == "/${var.project_name}/${var.environment}/NEXT_SERVER_GITHUB_CLIENT_SECRET"
    error_message = "NEXT_SERVER_GITHUB_CLIENT_SECRET must follow path: /{project}/{environment}/NEXT_SERVER_GITHUB_CLIENT_SECRET."
  }
}

run "test_next_server_github_client_secret_is_secure_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.next_server_github_client_secret.type == "SecureString"
    error_message = "NEXT_SERVER_GITHUB_CLIENT_SECRET must be stored as SecureString."
  }
}

run "test_next_server_graphql_url_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.next_server_graphql_url.name == "/${var.project_name}/${var.environment}/NEXT_SERVER_GRAPHQL_URL"
    error_message = "NEXT_SERVER_GRAPHQL_URL must follow path: /{project}/{environment}/NEXT_SERVER_GRAPHQL_URL."
  }
}

run "test_next_server_graphql_url_is_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.next_server_graphql_url.type == "String"
    error_message = "NEXT_SERVER_GRAPHQL_URL must be stored as String."
  }
}

run "test_nextauth_secret_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.nextauth_secret.name == "/${var.project_name}/${var.environment}/NEXTAUTH_SECRET"
    error_message = "NEXTAUTH_SECRET must follow path: /{project}/{environment}/NEXTAUTH_SECRET."
  }
}

run "test_nextauth_secret_is_secure_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.nextauth_secret.type == "SecureString"
    error_message = "NEXTAUTH_SECRET must be stored as SecureString."
  }
}

run "test_nextauth_url_path_format" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.nextauth_url.name == "/${var.project_name}/${var.environment}/NEXTAUTH_URL"
    error_message = "NEXTAUTH_URL must follow path: /{project}/{environment}/NEXTAUTH_URL."
  }
}

run "test_nextauth_url_is_string" {
  command = plan
  assert {
    condition     = aws_ssm_parameter.nextauth_url.type == "String"
    error_message = "NEXTAUTH_URL must be stored as String."
  }
}

run "test_slack_bot_token_disabled_by_default" {
  command = plan
  assert {
    condition     = length(aws_ssm_parameter.slack_bot_token) == 0
    error_message = "SLACK_BOT_TOKEN must not be created when enable_additional_parameters is false."
  }
}

run "test_slack_bot_token_is_secure_string" {
  command = plan
  variables {
    enable_additional_parameters = true
  }
  assert {
    condition     = aws_ssm_parameter.slack_bot_token[0].type == "SecureString"
    error_message = "SLACK_BOT_TOKEN must be stored as SecureString."
  }
}

run "test_slack_bot_token_path_format" {
  command = plan
  variables {
    enable_additional_parameters = true
  }
  assert {
    condition     = aws_ssm_parameter.slack_bot_token[0].name == "/${var.project_name}/${var.environment}/SLACK_BOT_TOKEN_${var.slack_bot_token_suffix}"
    error_message = "SLACK_BOT_TOKEN must follow path: /{project}/{environment}/SLACK_BOT_TOKEN_{suffix}."
  }
}

run "test_django_secret_key_length" {
  command = plan
  assert {
    condition     = random_string.django_secret_key.length == 50
    error_message = "Django secret key must be 50 characters long."
  }
}

run "test_django_secret_key_has_special_chars" {
  command = plan
  assert {
    condition     = random_string.django_secret_key.special == true
    error_message = "Django secret key must include special characters."
  }
}

run "test_nextauth_secret_length" {
  command = plan
  assert {
    condition     = random_string.nextauth_secret.length == 32
    error_message = "NextAuth secret must be 32 characters long."
  }
}

run "test_nextauth_secret_has_special_chars" {
  command = plan
  assert {
    condition     = random_string.nextauth_secret.special == true
    error_message = "NextAuth secret must include special characters."
  }
}
