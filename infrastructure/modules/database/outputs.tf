output "db_instance_endpoint" {
  description = "The endpoint of the RDS instance"
  value       = aws_db_instance.main.endpoint
}

output "db_password" {
  description = "The password for the RDS database"
  value       = random_password.db_password[0].result
  sensitive   = true
}
