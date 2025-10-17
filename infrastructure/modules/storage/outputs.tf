output "zappa_s3_bucket_arn" {
  description = "The ARN of the S3 bucket for Zappa deployments"
  value       = aws_s3_bucket.zappa.arn
}
