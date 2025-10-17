variable "environment" {
  description = "The environment (e.g., staging, production)"
  type        = string
}

variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "zappa_s3_bucket" {
  description = "The name of the S3 bucket for Zappa deployments"
  type        = string
}
