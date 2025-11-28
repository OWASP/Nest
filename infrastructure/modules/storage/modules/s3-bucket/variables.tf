variable "abort_incomplete_multipart_upload_days" {
  description = "Specifies the number of days after which an incomplete multipart upload is aborted."
  type        = number
  default     = 7
}

variable "bucket_name" {
  description = "The name of the bucket"
  type        = string
}

variable "force_destroy" {
  description = "If true, deletes all objects from the bucket when the bucket is destroyed."
  type        = bool
  default     = false
}

variable "noncurrent_version_expiration_days" {
  description = "Specifies the number of days an object is noncurrent before it is expired."
  type        = number
  default     = 30
}

variable "tags" {
  description = "A map of tags to apply to all resources."
  type        = map(string)
  default     = {}
}
