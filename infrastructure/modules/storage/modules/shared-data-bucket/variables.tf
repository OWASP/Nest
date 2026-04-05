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

variable "public_read_object_key" {
  default     = "nest.dump"
  description = "S3 object key allowing anonymous s3:GetObject (default nest.dump at bucket root)."
  type        = string
}
