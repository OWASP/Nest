output "fixtures_read_only_policy_arn" {
  description = "The ARN of the fixtures read-only IAM policy"
  value       = aws_iam_policy.fixtures_read_only.arn
}

output "fixtures_s3_bucket_arn" {
  description = "The ARN of the S3 bucket for fixtures"
  value       = module.fixtures_bucket.arn
}

output "zappa_s3_bucket" {
  description = "The name of the S3 bucket for Zappa deployments"
  value       = module.zappa_bucket.bucket
}

output "zappa_s3_bucket_arn" {
  description = "The ARN of the S3 bucket for Zappa deployments"
  value       = module.zappa_bucket.arn
}
