output "key_arn" {
  description = "The ARN of the KMS key."
  value       = aws_kms_key.main.arn
}
