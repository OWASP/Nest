output "security_group_id" {
  description = "Security group ID for VPC endpoints."
  value       = length(aws_security_group.vpc_endpoints) > 0 ? aws_security_group.vpc_endpoints[0].id : null
}
