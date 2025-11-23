variable "allowed_hosts" {
  description = "The Django allowed hosts."
  type        = string
  default     = "*"
}

variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "configuration" {
  description = "The name of the Django configuration to use (e.g., Staging, Production)."
  type        = string
  default     = "Staging"
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

variable "environment" {
  description = "The environment (e.g., staging, production)."
  type        = string
}

variable "project_name" {
  description = "The name of the project."
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

variable "settings_module" {
  description = "The location of the Django settings module to use (e.g., settings.staging, settings.production)."
  type        = string
  default     = "settings.staging"
}
