output "repository_name" {
  description = "The name of the ECR cache repository."
  value       = aws_ecr_repository.main.name
}

output "repository_url" {
  description = "The URL of the ECR cache repository."
  value       = aws_ecr_repository.main.repository_url
}
