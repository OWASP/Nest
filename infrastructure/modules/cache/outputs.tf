output "redis_password_arn" {
  description = "The legacy SSM parameter ARN for the Redis password."
  value       = try(aws_ssm_parameter.django_redis_password[0].arn, null)
}

output "redis_password_secret_arn" {
  description = "The Secrets Manager ARN containing the Redis password."
  value       = aws_secretsmanager_secret.django_redis_password
}
