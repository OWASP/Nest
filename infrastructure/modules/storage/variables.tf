variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "environment" {
  description = "The environment (e.g., staging, production)"
  type        = string
}

variable "fixtures_s3_bucket" {
  description = "The name of the S3 bucket for fixtures"
  type        = string
}

variable "force_destroy_bucket" {
  description = "If true, deletes all objects from the bucket when the bucket is destroyed."
  type        = bool
  default     = false
}

variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "zappa_s3_bucket" {
  description = "The name of the S3 bucket for Zappa deployments"
  type        = string
}
