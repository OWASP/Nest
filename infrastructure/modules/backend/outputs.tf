output "ecs_cluster_name" {
  description = "The name of the backend ECS cluster."
  value       = aws_ecs_cluster.backend.name
}

output "ecs_service_name" {
  description = "The name of the backend ECS service."
  value       = aws_ecs_service.backend.name
}
