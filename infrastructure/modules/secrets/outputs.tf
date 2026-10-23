output "django_secret_arns" {
  description = "Map of backend credential names to Secrets Manager ARNs."
  value = merge(
    { DJANGO_SECRET_KEY = aws_secretsmanager_secret.django_secret_key.arn },
    { for name, secret in aws_secretsmanager_secret.external_runtime : name => secret.arn if name != "NEXT_SERVER_GITHUB_CLIENT_SECRET" }
  )
  depends_on = [aws_secretsmanager_secret_version.django_secret_key]
}

output "external_secret_names" {
  description = "Map of external credential names to their Secrets Manager names for cutover validation."
  value       = { for name in keys(local.external_runtime_secrets) : name => "/${var.project_name}/${var.environment}/${name}" }
}

output "frontend_secret_arns" {
  description = "Map of frontend credential names to Secrets Manager ARNs."
  value = {
    NEXT_SERVER_GITHUB_CLIENT_SECRET = aws_secretsmanager_secret.external_runtime["NEXT_SERVER_GITHUB_CLIENT_SECRET"].arn
    NEXTAUTH_SECRET                  = aws_secretsmanager_secret.nextauth_secret.arn
  }
  depends_on = [aws_secretsmanager_secret_version.nextauth_secret]
}
