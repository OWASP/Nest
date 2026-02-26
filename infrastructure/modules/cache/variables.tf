variable "auto_minor_version_upgrade" {
  description = "Whether minor engine upgrades will be applied automatically."
  type        = bool
  default     = true
}

variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "environment" {
  description = "The environment (e.g., staging, production)."
  type        = string
}

variable "kms_key_arn" {
  description = "The ARN of the KMS key."
  type        = string
}

variable "log_retention_in_days" {
  description = "The number of days to retain log events."
  type        = number
  default     = 90
}

variable "maintenance_window" {
  description = "The weekly time range for when maintenance on the cache cluster is performed."
  type        = string
  default     = "mon:05:00-mon:07:00"
}

variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "redis_engine_version" {
  description = "The version of the Redis engine."
  type        = string
}

variable "redis_node_type" {
  description = "The node type for the Redis cache."
  type        = string

  validation {
    condition     = can(regex("^cache\\.", var.redis_node_type))
    error_message = "redis_node_type must start with 'cache.' (e.g., cache.t3.micro, cache.r5.large)."
  }
}

variable "redis_num_cache_nodes" {
  description = "The number of cache nodes in the Redis cluster."
  type        = number

  validation {
    condition     = var.redis_num_cache_nodes >= 1
    error_message = "redis_num_cache_nodes must be at least 1."
  }
}

variable "redis_port" {
  description = "The port for the Redis cache."
  type        = number

  validation {
    condition     = var.redis_port > 0 && var.redis_port < 65536
    error_message = "redis_port must be between 1 and 65535."
  }
}

variable "security_group_ids" {
  description = "A list of security group IDs to associate with the Redis cache."
  type        = list(string)

  validation {
    condition     = length(var.security_group_ids) > 0
    error_message = "security_group_ids must contain at least one security group."
  }
}

variable "snapshot_retention_limit" {
  description = "The number of days for which automatic snapshots are retained."
  type        = number
  default     = 5

  validation {
    condition     = var.snapshot_retention_limit >= 0 && var.snapshot_retention_limit <= 30
    error_message = "snapshot_retention_limit must be between 0 and 30."
  }
}

variable "snapshot_window" {
  description = "The daily time range (in UTC) during which ElastiCache will begin taking a daily snapshot."
  type        = string
  default     = "03:00-05:00"
}

variable "subnet_ids" {
  description = "A list of subnet IDs for the cache subnet group."
  type        = list(string)

  validation {
    condition     = length(var.subnet_ids) > 0
    error_message = "subnet_ids must contain at least one subnet."
  }
}
