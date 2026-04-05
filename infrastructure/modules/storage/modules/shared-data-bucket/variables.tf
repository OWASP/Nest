variable "abort_incomplete_multipart_upload_days" {
  default     = 7
  description = "Days after which an incomplete multipart upload is aborted."
  type        = number
}

variable "bucket_name" {
  default     = "owasp-nest-shared-data"
  description = "Global S3 bucket name for OWASP Nest shared public data (must be unique per AWS account)."
  type        = string
}

variable "common_tags" {
  default     = {}
  description = "Tags applied to the bucket."
  type        = map(string)
}

variable "noncurrent_version_expiration_days" {
  default     = 120
  description = "Days a noncurrent object version is retained before expiration."
  type        = number
}

variable "public_read_object_key" {
  default     = "nest.dump"
  description = "S3 object key allowing anonymous s3:GetObject (default nest.dump at bucket root)."
  type        = string

  validation {
    condition     = !can(regex("[*?]", var.public_read_object_key))
    error_message = "public_read_object_key must be a literal object key and may not contain wildcards like * or ?."
  }
}
