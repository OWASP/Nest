variable "db_allocated_storage" {
  description = "The allocated storage for the RDS database in GB"
  type        = number
}

variable "db_engine_version" {
  description = "The version of the PostgreSQL engine"
  type        = string
}

variable "db_instance_class" {
  description = "The instance class for the RDS database"
  type        = string
}

variable "db_name" {
  description = "The name of the RDS database"
  type        = string
}

variable "db_password" {
  description = "The password for the RDS database"
  type        = string
  sensitive   = true
  default     = null
}

variable "db_subnet_ids" {
  description = "A list of subnet IDs for the DB subnet group"
  type        = list(string)
}

variable "db_username" {
  description = "The username for the RDS database"
  type        = string
}

variable "environment" {
  description = "The environment (e.g., staging, production)"
  type        = string
}

variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "security_group_ids" {
  description = "A list of security group IDs to associate with the RDS database"
  type        = list(string)
}

variable "db_storage_type" {
  description = "The storage type for the RDS database"
  type        = string
  default     = "gp3"
}

variable "db_backup_retention_period" {
  description = "The number of days to retain backups for"
  type        = number
  default     = 7
}

variable "proxy_security_group_ids" {
  description = "A list of security group IDs to associate with the RDS proxy"
  type        = list(string)
}
