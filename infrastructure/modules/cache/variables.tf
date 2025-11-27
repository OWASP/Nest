variable "auto_minor_version_upgrade" {
  description = "Determines whether minor engine upgrades will be applied automatically."
  type        = bool
  default     = true
}

variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "environment" {
  description = "The environment (e.g., staging, production)"
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
  description = "The name of the project"
  type        = string
}

variable "redis_engine_version" {
  description = "The version of the Redis engine"
  type        = string
}

variable "redis_node_type" {
  description = "The node type for the Redis cache"
  type        = string
}

variable "redis_num_cache_nodes" {
  description = "The number of cache nodes in the Redis cluster"
  type        = number
}

variable "redis_port" {
  description = "The port for the Redis cache"
  type        = number
}

variable "security_group_ids" {
  description = "A list of security group IDs to associate with the Redis cache"
  type        = list(string)
}

variable "snapshot_retention_limit" {
  description = "The number of days for which automatic snapshots are retained."
  type        = number
  default     = 5
}

variable "snapshot_window" {
  description = "The daily time range (in UTC) during which ElastiCache will begin taking a daily snapshot."
  type        = string
  default     = "03:00-05:00"
}

variable "subnet_ids" {
  description = "A list of subnet IDs for the cache subnet group"
  type        = list(string)
}
