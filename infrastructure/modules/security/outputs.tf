output "alb_sg_id" {
  description = "The ID of the ALB security group."
  value       = aws_security_group.alb.id
}

output "frontend_sg_id" {
  description = "The ID of the frontend ECS security group."
  value       = aws_security_group.frontend.id
}

output "backend_sg_id" {
  description = "The ID of the backend ECS security group."
  value       = aws_security_group.backend.id
}

output "rds_proxy_sg_id" {
  description = "The ID of the RDS proxy security group."
  value       = var.create_rds_proxy ? aws_security_group.rds_proxy[0].id : null
}

output "rds_sg_id" {
  description = "The ID of the RDS security group."
  value       = aws_security_group.rds.id
}

output "redis_sg_id" {
  description = "The ID of the Redis security group."
  value       = aws_security_group.redis.id
}

output "tasks_sg_id" {
  description = "The ID of the ECS tasks security group."
  value       = aws_security_group.tasks.id
}
