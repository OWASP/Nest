variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "db_port" {
  description = "The port for the RDS database."
  type        = number

  validation {
    condition     = var.db_port > 0 && var.db_port < 65536
    error_message = "db_port must be between 1 and 65535."
  }
}

variable "enable_rds_proxy" {
  description = "Whether to create an RDS proxy."
  type        = bool
  default     = false
}

variable "enable_vpc_endpoint_rules" {
  description = "Whether to create security group rules for VPC endpoints."
  type        = bool
  default     = false
}

variable "environment" {
  description = "The environment (e.g., staging, production)."
  type        = string
}

variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "redis_port" {
  description = "The port for the Redis cache."
  type        = number

  validation {
    condition     = var.redis_port > 0 && var.redis_port < 65536
    error_message = "redis_port must be between 1 and 65535."
  }
}

variable "vpc_endpoint_sg_id" {
  description = "Security group ID for VPC endpoints (null if VPC endpoints disabled)."
  type        = string
  default     = null
}

variable "vpc_id" {
  description = "The ID of the VPC."
  type        = string
}
