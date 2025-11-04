variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "db_host" {
  description = "The hostname of the database."
  type        = string
}

variable "db_name" {
  description = "The name of the database."
  type        = string
}

variable "db_password" {
  description = "The password of the database."
  type        = string
  sensitive   = true
}

variable "db_port" {
  description = "The port of the database."
  type        = string
}

variable "db_user" {
  description = "The user for the database."
  type        = string
}

variable "redis_host" {
  description = "The hostname of the Redis cache."
  type        = string
}

variable "redis_password" {
  description = "The password of the Redis cache."
  type        = string
  sensitive   = true
}

variable "environment" {
  description = "The environment (e.g., staging, production)."
  type        = string
}

variable "project_name" {
  description = "The name of the project."
  type        = string
}
