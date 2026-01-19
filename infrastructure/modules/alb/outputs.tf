output "acm_certificate_arn" {
  description = "The ARN of the ACM certificate."
  value       = var.enable_https && var.domain_name != null ? aws_acm_certificate.main[0].arn : null
}

output "acm_certificate_domain_validation_options" {
  description = "The domain validation options for ACM certificate DNS validation."
  value       = var.enable_https && var.domain_name != null ? aws_acm_certificate.main[0].domain_validation_options : []
}

output "acm_certificate_status" {
  description = "The status of the ACM certificate."
  value       = var.enable_https && var.domain_name != null ? aws_acm_certificate.main[0].status : null
}

output "alb_arn" {
  description = "The ARN of the ALB."
  value       = aws_lb.main.arn
}

output "alb_dns_name" {
  description = "The DNS name of the ALB."
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "The zone ID of the ALB."
  value       = aws_lb.main.zone_id
}

output "frontend_target_group_arn" {
  description = "The ARN of the frontend target group."
  value       = aws_lb_target_group.frontend.arn
}

output "http_listener_arn" {
  description = "The ARN of the HTTP listener."
  value       = var.enable_https ? aws_lb_listener.http_redirect[0].arn : aws_lb_listener.http[0].arn
}

output "https_listener_arn" {
  description = "The ARN of the HTTPS listener (null if HTTPS disabled)."
  value       = var.enable_https ? aws_lb_listener.https[0].arn : null
}
