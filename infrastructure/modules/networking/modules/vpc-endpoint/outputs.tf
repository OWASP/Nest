output "security_group_id" {
  description = "Security group ID for VPC interface endpoints, or null when no interface endpoints are enabled."
  value       = length(aws_security_group.vpc_endpoints) > 0 ? aws_security_group.vpc_endpoints[0].id : null
}
