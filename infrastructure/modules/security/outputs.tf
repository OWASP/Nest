output "ecs_sg_id" {
  description = "The ID of the ECS security group"
  value       = aws_security_group.ecs.id
}

output "lambda_sg_id" {
  description = "The ID of the Lambda security group"
  value       = aws_security_group.lambda.id
}

output "rds_proxy_sg_id" {
  description = "The ID of the RDS proxy security group"
  value       = var.create_rds_proxy ? aws_security_group.rds_proxy[0].id : null
}

output "rds_sg_id" {
  description = "The ID of the RDS security group"
  value       = aws_security_group.rds.id
}

output "redis_sg_id" {
  description = "The ID of the Redis security group"
  value       = aws_security_group.redis.id
}
