variable "aws_region" {
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "us-east-2"
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
