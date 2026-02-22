output "dynamodb_table_names" {
  description = "The names of the per-environment DynamoDB tables for Terraform state locking."
  value       = { for env, table in aws_dynamodb_table.state_lock : env => table.name }
}

output "state_bucket_names" {
  description = "The names of the per-environment S3 buckets for Terraform state."
  value       = { for env, bucket in aws_s3_bucket.state : env => bucket.bucket }
}
