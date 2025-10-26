output "database_endpoint" {
  description = "The endpoint of the RDS proxy"
  value       = module.database.db_proxy_endpoint
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

output "private_subnet_ids" {
  description = "A list of private subnet IDs"
  value       = module.networking.private_subnet_ids
}

output "lambda_security_group_id" {
  description = "The ID of the security group for the Lambda function"
  value       = module.security.lambda_sg_id
}

output "ecr_repository_url" {
  description = "The URL of the ECR repository"
  value       = module.ecs.ecr_repository_url
}

output "zappa_s3_bucket" {
  description = "The name of the S3 bucket for Zappa deployments"
  value       = module.storage.zappa_s3_bucket.bucket
}
