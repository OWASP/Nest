output "db_proxy_endpoint" {
  description = "The endpoint of the RDS proxy"
  value       = aws_db_proxy.main.endpoint
}

output "db_password" {
  description = "The password for the RDS database"
  value       = random_password.db_password[0].result
  sensitive   = true
}
