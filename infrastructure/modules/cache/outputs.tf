output "redis_password_arn" {
  description = "The SSM Parameter ARN of password of Redis."
  value       = aws_ssm_parameter.django_redis_password.arn
}

output "redis_primary_endpoint" {
  description = "The primary endpoint of the Redis replication group."
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
}
