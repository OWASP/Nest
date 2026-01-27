output "key_alias_arn" {
  description = "The ARN of the KMS key alias."
  value       = aws_kms_alias.main.arn
}

output "key_alias_name" {
  description = "The name of the KMS key alias."
  value       = aws_kms_alias.main.name
}

output "key_arn" {
  description = "The ARN of the KMS key."
  value       = aws_kms_key.main.arn
}

output "key_id" {
  description = "The globally unique identifier for the KMS key."
  value       = aws_kms_key.main.key_id
}
