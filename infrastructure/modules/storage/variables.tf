variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "environment" {
  description = "The environment (e.g., staging, production)."
  type        = string
}

variable "fixtures_bucket_name" {
  description = "The name of the S3 bucket for fixtures."
  type        = string
}

variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "zappa_bucket_name" {
  description = "The name of the S3 bucket for Zappa deployments."
  type        = string
}
