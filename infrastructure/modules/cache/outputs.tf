output "redis_primary_endpoint" {
  description = "The primary endpoint of the Redis replication group."
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
}

output "redis_password_secret_arn" {
  description = "The ARN of the Redis password secret."
  value       = aws_secretsmanager_secret.django_redis_password.arn
  depends_on  = [aws_secretsmanager_secret_version.django_redis_password]
}
