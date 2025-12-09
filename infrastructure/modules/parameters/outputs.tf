output "django_ssm_parameter_arns" {
  description = "Map of environment variable names to the ARNs of all SSM parameters (Required by Django)."
  value = {
    "DJANGO_ALGOLIA_APPLICATION_ID"  = aws_ssm_parameter.django_algolia_application_id.arn
    "DJANGO_ALGOLIA_WRITE_API_KEY"   = aws_ssm_parameter.django_algolia_write_api_key.arn
    "DJANGO_ALLOWED_HOSTS"           = aws_ssm_parameter.django_allowed_hosts.arn
    "DJANGO_ALLOWED_ORIGINS"         = aws_ssm_parameter.django_allowed_origins.arn
    "DJANGO_CONFIGURATION"           = aws_ssm_parameter.django_configuration.arn
    "DJANGO_CSRF_COOKIE_HTTPONLY"    = aws_ssm_parameter.django_csrf_cookie_httponly.arn
    "DJANGO_CSRF_COOKIE_SAMESITE"    = aws_ssm_parameter.django_csrf_cookie_samesite.arn
    "DJANGO_DB_HOST"                 = aws_ssm_parameter.django_db_host.arn
    "DJANGO_DB_NAME"                 = aws_ssm_parameter.django_db_name.arn
    "DJANGO_DB_PASSWORD"             = var.db_password_arn
    "DJANGO_DB_PORT"                 = aws_ssm_parameter.django_db_port.arn
    "DJANGO_DB_USER"                 = aws_ssm_parameter.django_db_user.arn
    "DJANGO_OPEN_AI_SECRET_KEY"      = aws_ssm_parameter.django_open_ai_secret_key.arn
    "DJANGO_REDIS_HOST"              = aws_ssm_parameter.django_redis_host.arn
    "DJANGO_REDIS_PASSWORD"          = var.redis_password_arn
    "DJANGO_SECRET_KEY"              = aws_ssm_parameter.django_secret_key.arn
    "DJANGO_SENTRY_DSN"              = aws_ssm_parameter.django_sentry_dsn.arn
    "DJANGO_SESSION_COOKIE_SAMESITE" = aws_ssm_parameter.django_session_cookie_samesite.arn
    "DJANGO_SETTINGS_MODULE"         = aws_ssm_parameter.django_settings_module.arn
    "DJANGO_SLACK_BOT_TOKEN"         = aws_ssm_parameter.django_slack_bot_token.arn
    "DJANGO_SLACK_SIGNING_SECRET"    = aws_ssm_parameter.django_slack_signing_secret.arn
  }
}

output "frontend_ssm_parameter_arns" {
  description = "Map of frontend environment variable names to the ARNs of all SSM parameters."
  value = {
    "NEXT_SERVER_CSRF_URL"             = aws_ssm_parameter.next_server_csrf_url.arn
    "NEXT_SERVER_DISABLE_SSR"          = aws_ssm_parameter.next_server_disable_ssr.arn
    "NEXT_SERVER_GITHUB_CLIENT_ID"     = aws_ssm_parameter.next_server_github_client_id.arn
    "NEXT_SERVER_GITHUB_CLIENT_SECRET" = aws_ssm_parameter.next_server_github_client_secret.arn
    "NEXT_SERVER_GRAPHQL_URL"          = aws_ssm_parameter.next_server_graphql_url.arn
    "NEXTAUTH_SECRET"                  = aws_ssm_parameter.nextauth_secret.arn
    "NEXTAUTH_URL"                     = aws_ssm_parameter.nextauth_url.arn
  }
}
