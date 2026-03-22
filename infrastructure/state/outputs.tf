output "kms_key_aliases" {
  description = "The aliases of the per-environment KMS keys for Terraform state encryption."
  value       = { for env, kms in module.kms : env => kms.key_alias }
}

output "kms_key_arns" {
  description = "The ARNs of the per-environment KMS keys for Terraform state encryption."
  value       = { for env, kms in module.kms : env => kms.key_arn }
}

output "state_bucket_names" {
  description = "The names of the per-environment S3 buckets for Terraform state."
  value       = { for env, bucket in aws_s3_bucket.state : env => bucket.bucket }
}
