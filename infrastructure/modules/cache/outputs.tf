output "redis_password_arn" {
  description = "The legacy SSM parameter ARN for the Redis password."
  value       = try(aws_ssm_parameter.django_redis_password[0].arn, null)
}

output "redis_password_secret_arn" {
  description = "The Secrets Manager ARN containing the Redis password."
  value       = aws_secretsmanager_secret.django_redis_password.arn
}

output "redis_primary_endpoint" {
  description = "The primary endpoint of the Redis replication group."
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
}