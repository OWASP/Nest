variable "aws_region" {
  description = "The AWS region."
  type        = string
}

variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
}

variable "create_cloudwatch_logs" {
  description = "Whether to create CloudWatch Logs VPC endpoint."
  type        = bool
  default     = false
}

variable "create_ecr_api" {
  description = "Whether to create ECR API VPC endpoint."
  type        = bool
  default     = false
}

variable "create_ecr_dkr" {
  description = "Whether to create ECR DKR VPC endpoint."
  type        = bool
  default     = false
}

variable "create_s3" {
  description = "Whether to create S3 VPC endpoint (Gateway, free)."
  type        = bool
  default     = true
}

variable "create_secretsmanager" {
  description = "Whether to create Secrets Manager VPC endpoint."
  type        = bool
  default     = false
}

variable "create_ssm" {
  description = "Whether to create SSM VPC endpoint."
  type        = bool
  default     = false
}

variable "environment" {
  description = "The environment (e.g., staging, production)."
  type        = string
}

variable "private_route_table_id" {
  description = "The ID of the private route table."
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

variable "public_route_table_id" {
  description = "The ID of the public route table."
  type        = string
}

variable "vpc_cidr" {
  description = "The CIDR block for the VPC."
  type        = string

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "The vpc_cidr must be a valid IPv4 CIDR block."
  }
}

variable "vpc_id" {
  description = "The ID of the VPC."
  type        = string
}
