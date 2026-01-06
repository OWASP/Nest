output "backend_ecr_repository_url" {
  description = "The URL of the backend ECR repository."
  value       = module.ecs.ecr_repository_url
}

output "frontend_acm_certificate_status" {
  description = "The status of the frontend ACM certificate"
  value       = module.frontend.acm_certificate_status
}

output "frontend_acm_validation_records" {
  description = "The DNS validation records to add to the DNS provider for HTTPS."
  value       = module.frontend.acm_validation_records
}

output "frontend_alb_dns_name" {
  description = "The DNS name of the frontend ALB."
  value       = module.frontend.alb_dns_name
}

output "frontend_ecr_repository_url" {
  description = "The URL of the frontend ECR repository."
  value       = module.frontend.ecr_repository_url
}

output "frontend_url" {
  description = "The URL to access the frontend."
  value       = var.frontend_domain_name != null ? "https://${var.frontend_domain_name}" : "http://${module.frontend.alb_dns_name}"
}

output "private_subnet_ids" {
  description = "A list of private subnet IDs."
  value       = module.networking.private_subnet_ids
}

output "lambda_security_group_id" {
  description = "The ID of the security group for the Lambda function."
  value       = module.security.lambda_sg_id
}

output "zappa_s3_bucket" {
  description = "The name of the S3 bucket for Zappa deployments."
  value       = module.storage.zappa_s3_bucket.bucket
}
