output "acm_certificate_arn" {
  description = "The ARN of the ACM certificate."
  value       = var.enable_https && var.domain_name != null ? aws_acm_certificate.frontend[0].arn : null
}

output "acm_certificate_status" {
  description = "The status of the ACM certificate."
  value       = var.enable_https && var.domain_name != null ? aws_acm_certificate.frontend[0].status : null
}

output "acm_validation_records" {
  description = "The DNS validation records to add to your DNS provider."
  value = var.enable_https && var.domain_name != null ? {
    for domain_validation_option in aws_acm_certificate.frontend[0].domain_validation_options : domain_validation_option.domain_name => {
      name  = domain_validation_option.resource_record_name
      type  = domain_validation_option.resource_record_type
      value = domain_validation_option.resource_record_value
    }
  } : {}
}

output "alb_dns_name" {
  description = "The DNS name of the frontend ALB."
  value       = module.alb.alb_dns_name
}

output "alb_zone_id" {
  description = "The zone ID of the frontend ALB."
  value       = module.alb.alb_zone_id
}

output "ecr_repository_url" {
  description = "The URL of the frontend ECR repository."
  value       = aws_ecr_repository.frontend.repository_url
}

output "ecs_cluster_arn" {
  description = "The ARN of the ECS cluster."
  value       = aws_ecs_cluster.frontend.arn
}

output "ecs_cluster_name" {
  description = "The name of the ECS cluster."
  value       = aws_ecs_cluster.frontend.name
}

output "ecs_service_name" {
  description = "The name of the ECS service."
  value       = aws_ecs_service.frontend.name
}

output "target_group_arn" {
  description = "The ARN of the target group."
  value       = module.alb.target_group_arn
}
