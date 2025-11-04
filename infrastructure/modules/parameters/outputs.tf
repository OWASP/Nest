output "ssm_parameter_arns" {
  description = "Map of environment variable names to the ARNs of all SSM parameters."
  value = {
    "DJANGO_ALGOLIA_APPLICATION_ID" = aws_ssm_parameter.django_algolia_application_id.arn
    "DJANGO_ALGOLIA_WRITE_API_KEY"  = aws_ssm_parameter.django_algolia_write_api_key.arn
    "DJANGO_ALLOWED_HOSTS"          = aws_ssm_parameter.django_allowed_hosts.arn
    "DJANGO_AWS_ACCESS_KEY_ID"      = aws_ssm_parameter.django_aws_access_key_id.arn
    "DJANGO_AWS_SECRET_ACCESS_KEY"  = aws_ssm_parameter.django_aws_secret_access_key.arn
    "DJANGO_CONFIGURATION"          = aws_ssm_parameter.django_configuration.arn
    "DJANGO_DB_HOST"                = aws_ssm_parameter.django_db_host.arn
    "DJANGO_DB_NAME"                = aws_ssm_parameter.django_db_name.arn
    "DJANGO_DB_PASSWORD"            = aws_ssm_parameter.django_db_password.arn
    "DJANGO_DB_PORT"                = aws_ssm_parameter.django_db_port.arn
    "DJANGO_DB_USER"                = aws_ssm_parameter.django_db_user.arn
    "DJANGO_OPEN_AI_SECRET_KEY"     = aws_ssm_parameter.django_open_ai_secret_key.arn
    "DJANGO_REDIS_HOST"             = aws_ssm_parameter.django_redis_host.arn
    "DJANGO_REDIS_PASSWORD"         = aws_ssm_parameter.django_redis_password.arn
    "DJANGO_SECRET_KEY"             = aws_ssm_parameter.django_secret_key.arn
    "DJANGO_SENTRY_DSN"             = aws_ssm_parameter.django_sentry_dsn.arn
    "DJANGO_SETTINGS_MODULE"        = aws_ssm_parameter.django_settings_module.arn
    "DJANGO_SLACK_BOT_TOKEN"        = aws_ssm_parameter.django_slack_bot_token.arn
    "DJANGO_SLACK_SIGNING_SECRET"   = aws_ssm_parameter.django_slack_signing_secret.arn
  }
}
