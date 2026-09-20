variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "create_shared_data_bucket" {
  description = "Whether to create the shared public data S3 bucket."
  type        = bool
  default     = false
}

variable "environment" {
  description = "The environment (e.g., staging, production)."
  type        = string
}

variable "fixtures_bucket_name" {
  description = "The name of the S3 bucket for fixtures."
  type        = string
}

variable "kms_key_arn" {
  description = "The ARN of the KMS key (used for fixtures bucket encryption)."
  type        = string
}

variable "project_name" {
  description = "The name of the project."
  type        = string
}
