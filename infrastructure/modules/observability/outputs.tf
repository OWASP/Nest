output "grafana_security_group_id" {
  description = "Grafana security group ID for ALB integration, or null when the runtime is disabled."
  value       = one(aws_security_group.grafana[*].id)
}

output "grafana_service_name" {
  description = "Grafana ECS service name, or null when the runtime is disabled."
  value       = one(aws_ecs_service.grafana[*].name)
}

output "grafana_ecr_repository_arn" {
  description = "The ARN of the repository for the Grafana image."
  value       = aws_ecr_repository.grafana.arn
}

output "grafana_ecr_repository_url" {
  description = "The URL used to publish and pull the Grafana image."
  value       = aws_ecr_repository.grafana.repository_url
}

output "efs_file_system_id" {
  description = "The ID of the EFS file system backing VictoriaMetrics storage."
  value       = aws_efs_file_system.vm.id
}

output "vm_cluster_name" {
  description = "The name of the ECS cluster running VictoriaMetrics."
  value       = aws_ecs_cluster.vm.name
}

output "vm_endpoint" {
  description = "The private host:port endpoint for reaching VictoriaMetrics."
  value       = "${aws_service_discovery_service.vm.name}.${aws_service_discovery_private_dns_namespace.vm.name}:${var.vm_port}"
}

output "vm_security_group_id" {
  description = "The ID of the VictoriaMetrics security group."
  value       = aws_security_group.vm.id
}
