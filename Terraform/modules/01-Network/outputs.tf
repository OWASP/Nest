output "vpc_id" {
  description = "The ID of the created VPC."
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "A list of IDs for the public subnets."
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "A list of IDs for the private subnets."
  value       = aws_subnet.private[*].id
}

output "alb_security_group_id" {
  description = "The ID of the security group attached to the ALB."
  value       = aws_security_group.alb.id
}

output "alb_dns_name" {
  description = "The DNS name of the Application Load Balancer."
  value       = aws_lb.main.dns_name
}

output "alb_https_listener_arn" {
  description = "The ARN of the ALB's HTTPS listener."
  value       = aws_lb_listener.https.arn
}
