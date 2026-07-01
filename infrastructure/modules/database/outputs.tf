output "db_password_arn" {
  description = "The SSM Parameter ARN of password of the RDS database."
  value       = aws_ssm_parameter.django_db_password.arn
}
output "db_password-arn" {
  description = "The legacy SSM parameter ARN for the database password."
  value       = try(aws_ssm_parameter.django_db_password[0].arn, null)
}

output "db_credentials_secret_arn" {
  description = "The Secret Manager ARN containing the database credencials."
  value       = aws_secretsmanager_secret.db_credentials.arn
}

output "db_proxy_endpoint" {
  description = "The endpoint of the RDS proxy."
  value       = var.enable_rds_proxy ? aws_db_proxy.main[0].endpoint : aws_db_instance.main.address
}
