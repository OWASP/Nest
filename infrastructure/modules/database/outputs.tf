output "db_password" {
  description = "The password for the RDS database."
  value       = local.db_password
  sensitive   = true
}

output "db_proxy_endpoint" {
  description = "The endpoint of the RDS proxy."
  value       = var.create_rds_proxy ? aws_db_proxy.main[0].endpoint : aws_db_instance.main.address
}
