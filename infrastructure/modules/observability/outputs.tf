output "efs_file_system_id" {
  description = "The ID of the EFS file system backing observability storage."
  value       = aws_efs_file_system.vm.id
}

output "cluster_name" {
  description = "The name of the ECS cluster running the observability backend."
  value       = aws_ecs_cluster.vm.name
}

output "security_group_id" {
  description = "The ID of the observability backend security group."
  value       = aws_security_group.vm.id
}
