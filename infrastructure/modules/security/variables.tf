variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "create_rds_proxy" {
  description = "Whether to create an RDS proxy."
  type        = bool
  default     = false
}

variable "db_port" {
  description = "The port for the RDS database."
  type        = number
}

variable "default_egress_cidr_blocks" {
  description = "A list of CIDR blocks to allow for default egress traffic."
  type        = list(string)
  default     = ["0.0.0.0/0"]
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
}

variable "vpc_endpoint_sg_id" {
  description = "Security group ID for VPC endpoints."
  type        = string
}

variable "vpc_id" {
  description = "The ID of the VPC."
  type        = string
}
