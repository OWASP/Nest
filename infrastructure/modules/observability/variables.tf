variable "app_security_group_ids" {
  description = "Security group IDs of the application tasks allowed to send metrics to VictoriaMetrics."
  type        = list(string)

  validation {
    condition     = length(var.app_security_group_ids) > 0
    error_message = "app_security_group_ids must contain at least one security group."
  }
}

variable "assign_public_ip" {
  description = "Whether to assign a public IP to the VictoriaMetrics task."
  type        = bool
  default     = false
}

variable "aws_region" {
  description = "The AWS region where the module is deployed."
  type        = string
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
  description = "The ARN of the KMS key used to encrypt the EFS file system."
  type        = string
}

variable "log_retention_in_days" {
  description = "The number of days to retain VictoriaMetrics container logs."
  type        = number
  default     = 90
}

variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "subnet_ids" {
  description = "The private subnet IDs for the EFS mount targets and the VictoriaMetrics task."
  type        = list(string)

  validation {
    condition     = length(var.subnet_ids) > 0
    error_message = "subnet_ids must contain at least one subnet."
  }
}

variable "vm_cpu" {
  description = "The CPU units for the VictoriaMetrics Fargate task."
  type        = number
  default     = 512
}

variable "vm_desired_count" {
  description = "The number of VictoriaMetrics tasks to run (0 or 1; it is a single-node store)."
  type        = number
  default     = 1

  validation {
    condition     = contains([0, 1], var.vm_desired_count)
    error_message = "vm_desired_count must be 0 or 1 (VictoriaMetrics is a single-node store)."
  }
}

variable "vm_image" {
  description = "The VictoriaMetrics container image (including digest)."
  type        = string

  validation {
    condition     = can(regex("^[^@]+@sha256:[0-9a-f]{64}$", var.vm_image))
    error_message = "vm_image must be an image reference pinned to an immutable digest (e.g., repo:tag@sha256:...)."
  }
}

variable "vm_memory" {
  description = "The memory (in MiB) for the VictoriaMetrics Fargate task."
  type        = number
  default     = 1024
}

variable "vm_port" {
  description = "The port VictoriaMetrics listens on for ingest and queries."
  type        = number
  default     = 8428

  validation {
    condition     = var.vm_port > 0 && var.vm_port < 65536 && floor(var.vm_port) == var.vm_port
    error_message = "vm_port must be a whole number between 1 and 65535."
  }
}

variable "vm_retention_period" {
  description = "The VictoriaMetrics data retention period. A value without a suffix is in months, so the default \"12\" means 12 months (duration suffixes like 1y, 30d, 1w are also supported)."
  type        = string
  default     = "12" # 12 months
}

variable "vpc_id" {
  description = "The VPC ID where the VictoriaMetrics security group is created."
  type        = string
}
