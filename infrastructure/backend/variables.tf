variable "abort_incomplete_multipart_upload_days" {
  description = "Specifies the number of days after which an incomplete multipart upload is aborted."
  type        = number
  default     = 7
}

variable "aws_region" {
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "us-east-2"
}

variable "noncurrent_version_expiration_days" {
  description = "Specifies the number of days an object is noncurrent before it is expired."
  type        = number
  default     = 30
}

variable "project_name" {
  description = "The name of the project."
  type        = string
  default     = "owasp-nest"
}
