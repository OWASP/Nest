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

output "http_listener_arn" {
  description = "The ARN of the HTTP listener."
  value       = aws_lb_listener.http.arn
}

output "target_group_arn" {
  description = "The ARN of the target group."
  value       = aws_lb_target_group.main.arn
}
