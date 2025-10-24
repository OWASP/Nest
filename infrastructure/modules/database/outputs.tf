output "db_password" {
  description = "The password for the RDS database"
  value       = local.db_password
  sensitive   = true
}

output "db_proxy_endpoint" {
  description = "The endpoint of the RDS proxy"
  value       = aws_db_proxy.main.endpoint
}
