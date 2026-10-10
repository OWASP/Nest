resource "aws_secretsmanager_secret" "django_redis_password" {
  description             = "Redis authentication token used by Django."
  kms_key_id              = var.kms_key_arn
  name                    = "/${var.project_name}/${var.environment}/DJANGO_REDIS_PASSWORD"
  recovery_window_in_days = var.secret_recovery_window_in_days
  tags                    = var.common_tags
}

resource "aws_secretsmanager_secret_version" "django_redis_password" {
  secret_id     = aws_secretsmanager_secret.django_redis_password.id
  secret_string = local.redis_auth_token
}
