output "ecs_cluster_arn" {
  description = "The ARN of the ECS tasks cluster."
  value       = aws_ecs_cluster.main.arn
}

output "ecs_cluster_name" {
  description = "The name of the ECS tasks cluster."
  value       = aws_ecs_cluster.main.name
}

output "ecs_task_role_arn" {
  description = "The ARN of the ECS task role."
  value       = aws_iam_role.ecs_tasks_execution_role.arn
}
