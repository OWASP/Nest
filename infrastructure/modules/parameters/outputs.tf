output "django_container_secrets" {
  description = "Django environment variables mapped to ECS valueFrom references."
  sensitive   = true

  value = merge({
    "DJANGO_ALGOLIA_APPLICATION_ID"  = aws_ssm_parameter.django_algolia_application_id.arn
    "DJANGO_ALLOWED_HOSTS"           = aws_ssm_parameter.django_allowed_hosts.arn
    "DJANGO_ALLOWED_ORIGINS"         = aws_ssm_parameter.django_allowed_origins.arn
    "DJANGO_AWS_STORAGE_BUCKET_NAME" = aws_ssm_parameter.django_aws_storage_bucket_name.arn
    "DJANGO_CONFIGURATION"           = aws_ssm_parameter.django_configuration.arn
    "DJANGO_DB_HOST"                 = aws_ssm_parameter.django_db_host.arn
    "DJANGO_DB_NAME"                 = aws_ssm_parameter.django_db_name.arn
    "DJANGO_DB_PORT"                 = aws_ssm_parameter.django_db_port.arn
    "DJANGO_DB_USER"                 = aws_ssm_parameter.django_db_user.arn
    "DJANGO_REDIS_HOST"              = aws_ssm_parameter.django_redis_host.arn
    "DJANGO_REDIS_USE_TLS"           = aws_ssm_parameter.django_redis_use_tls.arn
    "DJANGO_RELEASE_VERSION"         = aws_ssm_parameter.django_release_version.arn
    "DJANGO_SETTINGS_MODULE"         = aws_ssm_parameter.django_settings_module.arn
    },
    var.enable_additional_parameters ? {
      "DJANGO_GITHUB_APP_ID"              = aws_ssm_parameter.django_github_app_id[0].arn
      "DJANGO_GITHUB_APP_INSTALLATION_ID" = aws_ssm_parameter.django_github_app_installation_id[0].arn
    } : {},
    var.runtime_secrets_mode == "prepare" ? merge(
      {
        "DJANGO_ALGOLIA_WRITE_API_KEY" = aws_ssm_parameter.django_algolia_write_api_key[0].arn
        "DJANGO_DB_PASSWORD"           = var.db_password_arn
        "DJANGO_OPEN_AI_SECRET_KEY"    = aws_ssm_parameter.django_open_ai_secret_key[0].arn
        "DJANGO_REDIS_PASSWORD"        = var.redis_password_arn
        "DJANGO_SECRET_KEY"            = aws_ssm_parameter.django_secret_key[0].arn
        "DJANGO_SENTRY_DSN"            = aws_ssm_parameter.django_sentry_dsn[0].arn
        "DJANGO_SLACK_BOT_TOKEN"       = aws_ssm_parameter.django_slack_bot_token[0].arn
        "DJANGO_SLACK_SIGNING_SECRET"  = aws_ssm_parameter.django_slack_signing_secret[0].arn
        "GITHUB_TOKEN"                 = aws_ssm_parameter.github_token[0].arn
      },
      var.enable_additional_parameters ? {
        "NEST_GITHUB_APP_PRIVATE_KEY"                   = aws_ssm_parameter.nest_github_app_private_key[0].arn
        "SLACK_BOT_TOKEN_${var.slack_bot_token_suffix}" = aws_ssm_parameter.slack_bot_token[0].arn
      } : {}
      ) : merge(
      {
        "DJANGO_ALGOLIA_WRITE_API_KEY" = aws_secretsmanager_secret.external_runtime["DJANGO_ALGOLIA_WRITE_API_KEY"].arn
        "DJANGO_DB_PASSWORD"           = "${var.db_credentials_secret_arn}:password::"
        "DJANGO_OPEN_AI_SECRET_KEY"    = aws_secretsmanager_secret.external_runtime["DJANGO_OPEN_AI_SECRET_KEY"].arn
        "DJANGO_REDIS_PASSWORD"        = var.redis_password_secret_arn
        "DJANGO_SECRET_KEY"            = aws_secretsmanager_secret.django_secret_key.arn
        "DJANGO_SENTRY_DSN"            = aws_secretsmanager_secret.external_runtime["DJANGO_SENTRY_DSN"].arn
        "DJANGO_SLACK_BOT_TOKEN"       = aws_secretsmanager_secret.external_runtime["DJANGO_SLACK_BOT_TOKEN"].arn
        "DJANGO_SLACK_SIGNING_SECRET"  = aws_secretsmanager_secret.external_runtime["DJANGO_SLACK_SIGNING_SECRET"].arn
        "GITHUB_TOKEN"                 = aws_secretsmanager_secret.external_runtime["GITHUB_TOKEN"].arn
      },
      var.enable_additional_parameters ? {
        "NEST_GITHUB_APP_PRIVATE_KEY"                   = aws_secretsmanager_secret.external_runtime["NEST_GITHUB_APP_PRIVATE_KEY"].arn
        "SLACK_BOT_TOKEN_${var.slack_bot_token_suffix}" = aws_secretsmanager_secret.external_runtime["SLACK_BOT_TOKEN_${var.slack_bot_token_suffix}"].arn
      } : {}
    )
  )
}

output "frontend_container_secrets" {
  description = "Frontend environment variables mapped to ECS valueFrom references."
  sensitive   = true

  value = merge(
    {
      "NEXT_SERVER_CSRF_URL"         = aws_ssm_parameter.next_server_csrf_url.arn
      "NEXT_SERVER_DISABLE_SSR"      = aws_ssm_parameter.next_server_disable_ssr.arn
      "NEXT_SERVER_GITHUB_CLIENT_ID" = aws_ssm_parameter.next_server_github_client_id.arn
      "NEXT_SERVER_GRAPHQL_URL"      = aws_ssm_parameter.next_server_graphql_url.arn
      "NEXTAUTH_URL"                 = aws_ssm_parameter.nextauth_url.arn
    },
    var.runtime_secrets_mode == "prepare" ? {
      "NEXT_SERVER_GITHUB_CLIENT_SECRET" = aws_ssm_parameter.next_server_github_client_secret[0].arn
      "NEXTAUTH_SECRET"                  = aws_ssm_parameter.nextauth_secret[0].arn
      } : {
      "NEXT_SERVER_GITHUB_CLIENT_SECRET" = aws_secretsmanager_secret.external_runtime["NEXT_SERVER_GITHUB_CLIENT_SECRET"].arn
      "NEXTAUTH_SECRET"                  = aws_secretsmanager_secret.nextauth_secret.arn
    }
  )
}

output "django_secretsmanager_secret_arns" {
  description = "Bare Secrets Manager ARNs required by Django ECS execution roles."

  value = var.runtime_secrets_mode == "complete" ? concat(
    [
      for name, secret in aws_secretsmanager_secret.external_runtime : secret.arn
      if name != "NEXT_SERVER_GITHUB_CLIENT_SECRET"
    ],
    [
      aws_secretsmanager_secret.django_secret_key.arn,
      var.db_credentials_secret_arn,
      var.redis_password_secret_arn,
    ]
  ) : []
}

output "frontend_secretsmanager_secret_arns" {
  description = "Bare Secrets Manager ARNs required by the frontend ECS execution role."

  value = var.runtime_secrets_mode == "complete" ? [
    aws_secretsmanager_secret.external_runtime["NEXT_SERVER_GITHUB_CLIENT_SECRET"].arn,
    aws_secretsmanager_secret.nextauth_secret.arn,
  ] : []
}
