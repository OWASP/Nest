output "dashboard_security_group_id" {
  description = "Dashboard security group ID for ALB integration, or null when the runtime is disabled."
  value       = one(aws_security_group.grafana[*].id)
}

output "dashboard_service_name" {
  description = "Dashboard ECS service name, or null when the runtime is disabled."
  value       = one(aws_ecs_service.grafana[*].name)
}

output "dashboard_ecr_repository_arn" {
  description = "The ARN of the repository for the dashboard image."
  value       = aws_ecr_repository.grafana.arn
}

output "dashboard_ecr_repository_url" {
  description = "The URL used to publish and pull the dashboard image."
  value       = aws_ecr_repository.grafana.repository_url
}

output "efs_file_system_id" {
  description = "The ID of the EFS file system backing observability storage."
  value       = aws_efs_file_system.vm.id
}

output "cluster_name" {
  description = "The name of the ECS cluster running the observability backend."
  value       = aws_ecs_cluster.vm.name
}

output "endpoint" {
  description = "The private host:port endpoint for reaching the observability backend."
  value       = "${aws_service_discovery_service.vm.name}.${aws_service_discovery_private_dns_namespace.vm.name}:${var.port}"
}

output "security_group_id" {
  description = "The ID of the observability backend security group."
  value       = aws_security_group.vm.id
}
