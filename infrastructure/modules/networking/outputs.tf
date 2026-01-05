output "vpc_id" {
  description = "The ID of the VPC."
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "A list of public subnet IDs."
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "A list of private subnet IDs."
  value       = aws_subnet.private[*].id
}

output "vpc_endpoint_security_group_id" {
  description = "Security group ID for VPC endpoints (null if disabled)."
  value       = var.create_vpc_endpoints ? module.vpc_endpoint[0].security_group_id : null
}
