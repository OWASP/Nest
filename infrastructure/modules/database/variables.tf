variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "db_allocated_storage" {
  description = "The allocated storage for the RDS database in GB"
  type        = number
}

variable "db_backup_retention_period" {
  description = "The number of days to retain backups for"
  type        = number
  default     = 7
}

variable "db_backup_window" {
  description = "The daily time range (in UTC) during which automated backups are created."
  type        = string
  default     = "03:00-04:00"
}

variable "db_copy_tags_to_snapshot" {
  description = "Specifies whether to copy all instance tags to snapshots."
  type        = bool
  default     = true
}

variable "db_enabled_cloudwatch_logs_exports" {
  description = "List of log types to export to CloudWatch Logs."
  type        = list(string)
  default     = ["postgresql", "upgrade"]
}

variable "db_engine_version" {
  description = "The version of the PostgreSQL engine"
  type        = string
}

variable "db_instance_class" {
  description = "The instance class for the RDS database"
  type        = string
}

variable "db_maintenance_window" {
  description = "The weekly time range (in UTC) during which system maintenance can occur."
  type        = string
  default     = "mon:04:00-mon:05:00"
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

variable "db_skip_final_snapshot" {
  description = "Determines whether a final DB snapshot is created before the DB instance is deleted."
  type        = bool
  default     = true
}

variable "db_storage_type" {
  description = "The storage type for the RDS database"
  type        = string
  default     = "gp3"
}

variable "db_subnet_ids" {
  description = "A list of subnet IDs for the DB subnet group"
  type        = list(string)
}

variable "db_user" {
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

variable "proxy_security_group_ids" {
  description = "A list of security group IDs to associate with the RDS proxy"
  type        = list(string)
}

variable "secret_recovery_window_in_days" {
  description = "The number of days that Secrets Manager waits before it can delete the secret. Set to 0 to delete immediately."
  type        = number
  default     = 0
}

variable "security_group_ids" {
  description = "A list of security group IDs to associate with the RDS database"
  type        = list(string)
}
