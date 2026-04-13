output "db_password_arn" {
  description = "The SSM Parameter ARN of password of the RDS database."
  value       = aws_ssm_parameter.django_db_password.arn
}

output "db_proxy_endpoint" {
  description = "The RDS proxy endpoint when proxying is enabled, otherwise the DB instance endpoint."
  value       = var.enable_rds_proxy ? aws_db_proxy.main[0].endpoint : aws_db_instance.main.address
}
