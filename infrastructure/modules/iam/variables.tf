variable "environment" {
  description = "The environment (e.g., staging, production)"
  type        = string
}

variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "s3_bucket_arn" {
  description = "The ARN of the S3 bucket for Zappa deployments"
  type        = string
}
