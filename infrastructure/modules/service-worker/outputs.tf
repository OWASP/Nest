output "ecs_service_name" {
  description = "The worker ECS service name."
  value       = aws_ecs_service.main.name
}

output "container_environment" {
  description = "Explicit environment variables passed to the worker container."
  sensitive   = true
  value       = try({ for entry in local.container_definition.environment : entry.name => entry.value }, {})
}
