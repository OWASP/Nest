output "db_proxy_endpoint" {
  description = "The endpoint of the RDS proxy."
  value       = var.enable_rds_proxy ? aws_db_proxy.main[0].endpoint : aws_db_instance.main.address
}

output "db_credentials_secret_arn" {
  description = "The ARN of the database credentials secret."
  value       = aws_secretsmanager_secret.db_credentials.arn
  depends_on  = [aws_secretsmanager_secret_version.db_credentials]
}
