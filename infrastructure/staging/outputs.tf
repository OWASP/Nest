output "acm_certificate_domain_validation_options" {
  description = "The DNS validation options for ACM certificate."
  value       = module.alb.acm_certificate_domain_validation_options
}

output "acm_certificate_status" {
  description = "The status of the ACM certificate."
  value       = module.alb.acm_certificate_status
}

output "alb_dns_name" {
  description = "The DNS name of the ALB."
  value       = module.alb.alb_dns_name
}

output "backend_ecr_repository_url" {
  description = "The URL of the backend ECR repository."
  value       = module.ecs.ecr_repository_url
}

output "ecs_security_group_id" {
  description = "The ID of the security group for ECS tasks."
  value       = module.security.ecs_sg_id
}

output "backend_cluster_name" {
  description = "The name of the ECS backend cluster."
  value       = module.backend.ecs_cluster_name
}

output "backend_service_name" {
  description = "The name of the ECS backend service."
  value       = module.backend.ecs_service_name
}

output "fixtures_bucket_name" {
  description = "The name of the S3 bucket for database fixtures."
  value       = module.storage.fixtures_s3_bucket_name
}

output "frontend_cluster_name" {
  description = "The name of the ECS frontend cluster."
  value       = module.frontend.ecs_cluster_name
}

output "frontend_ecr_repository_url" {
  description = "The URL of the frontend ECR repository."
  value       = module.frontend.ecr_repository_url
}

output "frontend_service_name" {
  description = "The name of the ECS frontend service."
  value       = module.frontend.ecs_service_name
}

output "frontend_url" {
  description = "The URL to access the frontend."
  value       = "https://${var.domain_name}"
}

output "private_subnet_ids" {
  description = "A list of private subnet IDs."
  value       = module.networking.private_subnet_ids
}

output "tasks_cluster_name" {
  description = "The name of the ECS tasks cluster."
  value       = module.ecs.ecs_cluster_name
}
