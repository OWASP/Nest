output "fixtures_read_only_policy_arn" {
  description = "The ARN of the fixtures read-only IAM policy"
  value       = aws_iam_policy.fixtures_read_only.arn
}

output "fixtures_s3_bucket_arn" {
  description = "The ARN of the S3 bucket for fixtures"
  value       = aws_s3_bucket.fixtures.arn
}

output "zappa_s3_bucket" {
  description = "The name of the S3 bucket for Zappa deployments"
  value       = aws_s3_bucket.zappa
}

output "zappa_s3_bucket_arn" {
  description = "The ARN of the S3 bucket for Zappa deployments"
  value       = aws_s3_bucket.zappa.arn
}
