output "bucket_arn" {
  description = "ARN of the OWASP Nest shared data S3 bucket."
  value       = aws_s3_bucket.nest_shared_data.arn
}

output "bucket_id" {
  description = "Name of the OWASP Nest shared data S3 bucket."
  value       = aws_s3_bucket.nest_shared_data.id
}
