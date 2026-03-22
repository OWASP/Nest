variable "abort_incomplete_multipart_upload_days" {
  description = "The number of days after which an incomplete multipart upload is aborted."
  type        = number
  default     = 7
}

variable "bucket_name" {
  description = "The name of the bucket."
  type        = string
}

variable "kms_key_arn" {
  description = "ARN of the KMS key for SSE-KMS encryption. If null, uses SSE-S3 (AES256) instead."
  type        = string
  default     = null
}

variable "allow_public_read" {
  description = "Whether to allow public read access to objects in the bucket."
  type        = bool
  default     = false
}

variable "noncurrent_version_expiration_days" {
  description = "The number of days an object is noncurrent before it is expired."
  type        = number
  default     = 30
}

variable "tags" {
  description = "A map of tags to apply to all resources."
  type        = map(string)
  default     = {}
}
