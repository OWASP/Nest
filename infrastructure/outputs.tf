output "database_endpoint" {
  description = "The endpoint of the RDS database"
  value       = module.database.db_instance_endpoint
}

output "redis_endpoint" {
  description = "The endpoint of the Redis cache"
  value       = module.cache.redis_primary_endpoint
}

output "db_password" {
  description = "The password for the RDS database"
  value       = module.database.db_password
  sensitive   = true
}

output "redis_auth_token" {
  description = "The auth token for Redis"
  value       = module.cache.redis_auth_token
  sensitive   = true
}
