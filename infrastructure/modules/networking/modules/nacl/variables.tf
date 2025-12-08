variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
}

variable "environment" {
  description = "The environment (e.g., staging, production)."
  type        = string
}

variable "private_subnet_ids" {
  description = "A list of private subnet IDs."
  type        = list(string)
}

variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "public_subnet_ids" {
  description = "A list of public subnet IDs."
  type        = list(string)
}

variable "vpc_cidr" {
  description = "The CIDR block for the VPC."
  type        = string
}

variable "vpc_id" {
  description = "The ID of the VPC."
  type        = string
}
