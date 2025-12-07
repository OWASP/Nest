output "db_password_arn" {
  description = "The SSM Parameter ARN of password of the RDS database."
  value       = aws_ssm_parameter.django_db_password.arn
}

output "db_proxy_endpoint" {
  description = "The endpoint of the RDS proxy."
  value       = var.create_rds_proxy ? aws_db_proxy.main[0].endpoint : aws_db_instance.main.address
}
