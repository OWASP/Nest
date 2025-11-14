variable "project_prefix" {
  description = "A prefix used for naming all resources, e.g., 'owasp-nest'."
  type        = string
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_prefix))
    error_message = "The project_prefix must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "environment" {
  description = "The deployment environment (e.g., 'dev', 'staging', 'prod')."
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "The environment must be one of: dev, staging, prod."
  }
}
variable "vpc_cidr" {
  description = "The CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "A list of Availability Zones to deploy resources into. Must match the number of subnets. e.g., [\"us-east-1a\", \"us-east-1b\"]"
  type        = list(string)
}

variable "public_subnet_cidrs" {
  description = "A list of CIDR blocks for the public subnets. The number of CIDRs must match the number of availability_zones."
  type        = list(string)
  validation {
    condition     = length(var.public_subnet_cidrs) > 0
    error_message = "Provide at least one public subnet CIDR, and ensure its count matches availability_zones."
  }
}

variable "private_subnet_cidrs" {
  description = "A list of CIDR blocks for the private subnets. The number of CIDRs must match the number of availability_zones."
  type        = list(string)
  validation {
    condition     = length(var.private_subnet_cidrs) > 0
    error_message = "Provide at least one private subnet CIDR, and ensure its count matches availability_zones."
  }
}

variable "acm_certificate_arn" {
  description = "The ARN of the AWS Certificate Manager (ACM) certificate for the ALB's HTTPS listener."
  type        = string
  # No default value, this must be provided by the root module.
}

variable "tags" {
  description = "A map of tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "enable_alb_access_logs" {
  description = "Set to true to enable access logging for the Application Load Balancer."
  type        = bool
  default     = true
}

variable "alb_access_logs_bucket_name" {
  description = "The name of the S3 bucket to store ALB access logs. Must be globally unique. If left empty, a name will be generated."
  type        = string
  default     = ""
}
