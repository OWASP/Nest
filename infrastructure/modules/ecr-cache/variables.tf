variable "common_tags" {
  description = "Common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "name" {
  description = "The ECR repository name for build cache manifests."
  type        = string
}
