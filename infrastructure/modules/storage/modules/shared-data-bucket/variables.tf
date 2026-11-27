variable "abort_incomplete_multipart_upload_days" {
  default     = 7
  description = "Days after which an incomplete multipart upload is aborted."
  type        = number

  validation {
    condition = (
      var.abort_incomplete_multipart_upload_days >= 1 &&
      var.abort_incomplete_multipart_upload_days == floor(var.abort_incomplete_multipart_upload_days)
    )
    error_message = "abort_incomplete_multipart_upload_days must be a positive integer (whole days, at least 1)."
  }
}

variable "bucket_name" {
  default     = "owasp-nest-shared-data"
  description = "Global S3 bucket name for OWASP Nest shared public data."
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

  validation {
    condition = (
      var.noncurrent_version_expiration_days >= 1 &&
      var.noncurrent_version_expiration_days == floor(var.noncurrent_version_expiration_days)
    )
    error_message = "noncurrent_version_expiration_days must be a positive integer (whole days, at least 1)."
  }
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
