output "arn" {
  description = "The ARN of the S3 bucket."
  value       = aws_s3_bucket.this.arn
}

output "bucket" {
  description = "The S3 bucket resource."
  value       = aws_s3_bucket.this
}

output "server_side_encryption_configuration" {
  description = "The server-side encryption configuration."
  value       = aws_s3_bucket_server_side_encryption_configuration.this
}
