variable "aws_region" {
  description = "The AWS region."
  type        = string
}

variable "availability_zones" {
  description = "A list of availability zones for the VPC."
  type        = list(string)
}

variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "create_vpc_cloudwatch_logs_endpoint" {
  description = "Whether to create CloudWatch Logs VPC endpoint."
  type        = bool
  default     = false
}

variable "create_vpc_ecr_api_endpoint" {
  description = "Whether to create ECR API VPC endpoint."
  type        = bool
  default     = false
}

variable "create_vpc_ecr_dkr_endpoint" {
  description = "Whether to create ECR DKR VPC endpoint."
  type        = bool
  default     = false
}

variable "create_vpc_s3_endpoint" {
  description = "Whether to create S3 VPC endpoint (Gateway, free)."
  type        = bool
  default     = false
}

variable "create_vpc_secretsmanager_endpoint" {
  description = "Whether to create Secrets Manager VPC endpoint."
  type        = bool
  default     = false
}

variable "create_vpc_ssm_endpoint" {
  description = "Whether to create SSM VPC endpoint."
  type        = bool
  default     = false
}

variable "environment" {
  description = "The environment (e.g., staging, production)."
  type        = string
}

variable "log_retention_in_days" {
  description = "The number of days to retain log events."
  type        = number
  default     = 90
}

variable "private_subnet_cidrs" {
  description = "A list of CIDR blocks for the private subnets."
  type        = list(string)
}

variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "public_subnet_cidrs" {
  description = "A list of CIDR blocks for the public subnets."
  type        = list(string)
}

variable "vpc_cidr" {
  description = "The CIDR block for the VPC."
  type        = string
}
