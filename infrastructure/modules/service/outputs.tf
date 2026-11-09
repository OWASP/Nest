output "ecr_repository_arn" {
  description = "The ARN of the ECR repository."
  value       = aws_ecr_repository.main.arn
}

output "ecr_repository_url" {
  description = "The URL of the ECR repository."
  value       = aws_ecr_repository.main.repository_url
}

output "ecs_cluster_arn" {
  description = "The ARN of the ECS cluster."
  value       = aws_ecs_cluster.main.arn
}

output "ecs_cluster_name" {
  description = "The name of the ECS cluster."
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "The name of the ECS service."
  value       = aws_ecs_service.main.name
}

output "task_context" {
  description = "Shared configuration for workers using this service's release, cluster and roles."
  sensitive   = true
  value = {
    cluster_arn          = aws_ecs_cluster.main.arn
    execution_role_arn   = aws_iam_role.ecs_task_execution_role.arn
    task_role_arn        = aws_iam_role.ecs_task_role.arn
    cpu                  = var.container_cpu
    memory               = var.container_memory
    container_definition = local.container_definition
  }
  depends_on = [
    aws_iam_role_policy_attachment.ecs_task_execution_policy_attachment,
    aws_iam_role_policy_attachment.ecs_task_execution_ssm_policy_attachment,
    aws_iam_role_policy_attachment.task_role_policies,
    aws_iam_role_policy_attachment.ecs_task_role_kms,
  ]
}

output "container_environment" {
  description = "Explicit environment variables passed to the web container."
  value       = try({ for entry in local.container_definition.environment : entry.name => entry.value }, {})
}

output "additional_task_role_policy_arns" {
  description = "Additional policy ARNs attached to the application task role."
  value = [
    for attachment in aws_iam_role_policy_attachment.task_role_policies : attachment.policy_arn
    if attachment.role == aws_iam_role.ecs_task_role.name
  ]
}
