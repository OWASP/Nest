variable "abort_incomplete_multipart_upload_days" {
  description = "Specifies the number of days after which an incomplete multipart upload is aborted."
  type        = number
  default     = 7
}

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

variable "noncurrent_version_expiration_days" {
  description = "Specifies the number of days an object is noncurrent before it is expired."
  type        = number
  default     = 30
}

variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "zappa_s3_bucket" {
  description = "The name of the S3 bucket for Zappa deployments"
  type        = string
}
