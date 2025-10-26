output "redis_auth_token" {
  description = "The auth token for Redis"
  value       = random_password.redis_auth_token[0].result
  sensitive   = true
}

output "redis_primary_endpoint" {
  description = "The primary endpoint of the Redis replication group"
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
}
