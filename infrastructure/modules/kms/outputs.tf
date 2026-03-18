output "key_alias" {
  description = "The alias of the KMS key."
  value       = aws_kms_alias.main.name
}

output "key_arn" {
  description = "The ARN of the KMS key."
  value       = aws_kms_key.main.arn
}
