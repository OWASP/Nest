variable "abort_incomplete_multipart_upload_days" {
  description = "The number of days after which an incomplete multipart upload is aborted."
  type        = number
  default     = 7
}

variable "aws_region" {
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "us-east-2"
}

variable "expire_log_days" {
  description = "The number of days to expire logs after."
  type        = number
  default     = 90
}

variable "noncurrent_version_expiration_days" {
  description = "The number of days an object is noncurrent before it is expired."
  type        = number
  default     = 30
}

variable "project_name" {
  description = "The name of the project."
  type        = string
  default     = "owasp-nest"
}
