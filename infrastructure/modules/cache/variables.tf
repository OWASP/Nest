variable "environment" {
  description = "The environment (e.g., staging, production)"
  type        = string
}

variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "redis_auth_token" {
  description = "The auth token for Redis"
  type        = string
  sensitive   = true
  default     = null
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

variable "subnet_ids" {
  description = "A list of subnet IDs for the cache subnet group"
  type        = list(string)
}
