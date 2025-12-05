variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs"
  type        = list(string)
}

variable "project_name" {
  description = "Project name"
  type        = string
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs"
  type        = list(string)
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}
