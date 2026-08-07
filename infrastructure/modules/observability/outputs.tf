output "efs_file_system_id" {
  description = "The ID of the EFS file system backing VictoriaMetrics storage."
  value       = aws_efs_file_system.vm.id
}

output "vm_cluster_name" {
  description = "The name of the ECS cluster running VictoriaMetrics."
  value       = aws_ecs_cluster.vm.name
}

output "vm_security_group_id" {
  description = "The ID of the VictoriaMetrics security group."
  value       = aws_security_group.vm.id
}
