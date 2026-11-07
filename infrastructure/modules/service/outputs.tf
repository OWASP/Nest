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

output "ecs_worker_service_name" {
  description = "The optional queue worker service name."
  value       = one(aws_ecs_service.worker[*].name)
}

output "container_environments" {
  description = "Explicit environment variables passed to the web and optional worker containers."
  value = {
    web    = try({ for entry in local.container_definition.environment : entry.name => entry.value }, {})
    worker = try({ for entry in local.worker_definition.environment : entry.name => entry.value }, {})
  }
}

output "additional_task_role_policy_arns" {
  description = "Additional policy ARNs attached to the application task role."
  value = [
    for attachment in aws_iam_role_policy_attachment.task_role_policies : attachment.policy_arn
    if attachment.role == aws_iam_role.ecs_task_role.name
  ]
}
