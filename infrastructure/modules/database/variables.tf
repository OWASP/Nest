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

variable "db_allocated_storage" {
  description = "The allocated storage for the RDS database in GB."
  type        = number

  validation {
    condition     = var.db_allocated_storage >= 20
    error_message = "db_allocated_storage must be at least 20 GB."
  }
}

variable "db_backup_retention_period" {
  description = "The number of days to retain backups for."
  type        = number
  default     = 7

  validation {
    condition     = var.db_backup_retention_period >= 0 && var.db_backup_retention_period <= 35
    error_message = "db_backup_retention_period must be between 0 and 35."
  }
}

variable "db_backup_window" {
  description = "The daily time range (in UTC) during which automated backups are created."
  type        = string
  default     = "03:00-04:00"
}

variable "db_copy_tags_to_snapshot" {
  description = "Whether to copy all instance tags to snapshots."
  type        = bool
  default     = true
}

variable "db_deletion_protection" {
  description = "Specifies whether to prevent database deletion."
  type        = bool
  default     = true
}

variable "db_enabled_cloudwatch_logs_exports" {
  description = "List of log types to export to CloudWatch Logs."
  type        = list(string)
  default     = ["postgresql", "upgrade"]
}

variable "db_engine_version" {
  description = "The version of the PostgreSQL engine."
  type        = string
}

variable "db_instance_class" {
  description = "The instance class for the RDS database."
  type        = string

  validation {
    condition     = can(regex("^db\\.", var.db_instance_class))
    error_message = "db_instance_class must start with 'db.' (e.g., db.t3.micro, db.r5.large)."
  }
}

variable "db_maintenance_window" {
  description = "The weekly time range (in UTC) during which system maintenance can occur."
  type        = string
  default     = "mon:04:00-mon:05:00"
}

variable "db_name" {
  description = "The name of the RDS database."
  type        = string
}

variable "db_password" {
  description = "The password for the RDS database."
  type        = string
  sensitive   = true
  default     = null
}

variable "db_skip_final_snapshot" {
  description = "Whether a final DB snapshot is created before the DB instance is deleted."
  type        = bool
  default     = false
}

variable "db_storage_type" {
  description = "The storage type for the RDS database."
  type        = string
  default     = "gp3"

  validation {
    condition     = contains(["gp2", "gp3", "io1", "io2"], var.db_storage_type)
    error_message = "db_storage_type must be one of: gp2, gp3, io1, io2."
  }
}

variable "db_subnet_ids" {
  description = "A list of subnet IDs for the DB subnet group."
  type        = list(string)

  validation {
    condition     = length(var.db_subnet_ids) > 0
    error_message = "db_subnet_ids must contain at least one subnet."
  }
}

variable "db_user" {
  description = "The username for the RDS database."
  type        = string
}

variable "environment" {
  description = "The environment (e.g., staging, production)."
  type        = string
}

variable "kms_key_arn" {
  description = "The ARN of the KMS key."
  type        = string
}

variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "proxy_security_group_ids" {
  description = "A list of security group IDs to associate with the RDS proxy."
  type        = list(string)
  default     = []
}

variable "secret_recovery_window_in_days" {
  description = "The number of days that Secrets Manager waits before it can delete the secret. Set to 0 to delete immediately."
  type        = number
  default     = 7

  validation {
    condition     = var.secret_recovery_window_in_days == 0 || (var.secret_recovery_window_in_days >= 7 && var.secret_recovery_window_in_days <= 30)
    error_message = "secret_recovery_window_in_days must be 0 or between 7 and 30."
  }
}

variable "security_group_ids" {
  description = "A list of security group IDs to associate with the RDS database."
  type        = list(string)

  validation {
    condition     = length(var.security_group_ids) > 0
    error_message = "security_group_ids must contain at least one security group."
  }
}
