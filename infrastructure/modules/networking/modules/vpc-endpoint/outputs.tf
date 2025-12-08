output "security_group_id" {
  description = "Security group ID for VPC endpoints."
  value       = aws_security_group.vpc_endpoints.id
}
