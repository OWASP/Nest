variable "aws_region" {
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "us-east-2"
}

variable "aws_role_external_id" {
  description = "The external ID for role assumption."
  type        = string
}

variable "environments" {
  description = "The environments to create Terraform roles for."
  type        = list(string)
  default     = ["staging"]
}

variable "project_name" {
  description = "The name of the project."
  type        = string
  default     = "nest"
}
