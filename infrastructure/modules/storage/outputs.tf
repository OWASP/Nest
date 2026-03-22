output "fixtures_read_only_policy_arn" {
  description = "The ARN of the fixtures read-only IAM policy."
  value       = aws_iam_policy.fixtures_read_only.arn
}

output "fixtures_s3_bucket_arn" {
  description = "The ARN of the S3 bucket for fixtures."
  value       = module.fixtures_bucket.arn
}

output "fixtures_s3_bucket_name" {
  description = "The name of the S3 bucket for fixtures."
  value       = module.fixtures_bucket.bucket.id
}

output "static_read_write_policy_arn" {
  description = "The ARN of the static files read/write IAM policy."
  value       = aws_iam_policy.static_read_write.arn
}

output "static_s3_bucket_name" {
  description = "The name of the S3 bucket for static files."
  value       = module.static_bucket.bucket.id
}
