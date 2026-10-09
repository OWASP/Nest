output "app_security_group_ids" {
  description = "The IDs of the stand-in application security groups."
  value       = aws_security_group.app[*].id
}

output "kms_key_arn" {
  description = "The ARN of the stand-in KMS key."
  value       = aws_kms_key.main.arn
}

output "subnet_ids" {
  description = "The IDs of the stand-in subnets."
  value       = aws_subnet.main[*].id
}

output "vpc_id" {
  description = "The ID of the stand-in VPC."
  value       = aws_vpc.main.id
}
