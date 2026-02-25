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

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid IPv4 CIDR block (e.g., 10.0.0.0/16)."
  }
}

variable "vpc_id" {
  description = "The ID of the VPC."
  type        = string
}
