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

variable "grafana_admin_password_parameter_arn" {
  description = "ARN of an externally managed SSM SecureString containing the initial Grafana admin password."
  type        = string
  default     = null
  validation {
    condition     = var.grafana_admin_password_parameter_arn == null ? true : can(regex("^arn:aws[a-z-]*:ssm:[a-z0-9-]+:[0-9]{12}:parameter/.+$", var.grafana_admin_password_parameter_arn))
    error_message = "Provide an SSM parameter ARN, not a plaintext password."
  }
}

variable "grafana_admin_password_kms_key_arn" {
  description = "Customer-managed KMS key ARN for the password parameter; null uses the AWS-managed SSM key."
  type        = string
  default     = null
  validation {
    condition = var.grafana_admin_password_kms_key_arn == null ? true : (
      var.grafana_admin_password_parameter_arn != null &&
      can(regex("^arn:aws[a-z-]*:kms:[a-z0-9-]+:[0-9]{12}:key/.+$", var.grafana_admin_password_kms_key_arn))
    )
    error_message = "A password KMS key requires a password parameter ARN and must be a KMS key ARN."
  }
}

variable "grafana_domain_name" {
  description = "Public Grafana hostname, without scheme or path; null leaves public URL configuration unset."
  type        = string
  default     = null
  validation {
    condition     = var.grafana_domain_name == null ? true : can(regex("^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$", var.grafana_domain_name))
    error_message = "Provide a lowercase DNS hostname, without https://, port, or path."
  }
}

variable "grafana_image" {
  description = "Digest-pinned Grafana image; null omits Grafana runtime resources."
  type        = string
  default     = null
  validation {
    condition     = var.grafana_image == null ? true : can(regex("^[^@]+@sha256:[0-9a-f]{64}$", var.grafana_image))
    error_message = "grafana_image must be null or an image reference pinned by SHA256 digest."
  }
}

variable "grafana_desired_count" {
  description = "Grafana task count (0 or 1). Keep zero until credentials and access are configured."
  type        = number
  default     = 0
  validation {
    condition     = contains([0, 1], var.grafana_desired_count) && (var.grafana_desired_count == 0 || (var.grafana_image != null && var.grafana_admin_password_parameter_arn != null))
    error_message = "Grafana supports zero or one task; starting requires an image and admin password parameter ARN."
  }
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
  description = "The VictoriaMetrics data retention period (e.g., 12, 5y)."
  type        = string
  default     = "12"
}

variable "vpc_id" {
  description = "The VPC ID where the VictoriaMetrics security group is created."
  type        = string
}
