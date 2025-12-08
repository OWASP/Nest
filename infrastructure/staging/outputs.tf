output "private_subnet_ids" {
  description = "A list of private subnet IDs."
  value       = module.networking.private_subnet_ids
}

output "lambda_security_group_id" {
  description = "The ID of the security group for the Lambda function."
  value       = module.security.lambda_sg_id
}

output "ecr_repository_url" {
  description = "The URL of the ECR repository."
  value       = module.ecs.ecr_repository_url
}

output "zappa_s3_bucket" {
  description = "The name of the S3 bucket for Zappa deployments."
  value       = module.storage.zappa_s3_bucket.bucket
}
