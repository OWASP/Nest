output "lambda_sg_id" {
  description = "The ID of the Lambda security group"
  value       = aws_security_group.lambda.id
}

output "rds_sg_id" {
  description = "The ID of the RDS security group"
  value       = aws_security_group.rds.id
}

output "redis_sg_id" {
  description = "The ID of the Redis security group"
  value       = aws_security_group.redis.id
}
