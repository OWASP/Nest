variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "deletion_window_in_days" {
  description = "The number of days before the KMS key is deleted after destruction."
  type        = number
  default     = 30

  validation {
    condition     = var.deletion_window_in_days >= 7 && var.deletion_window_in_days <= 30
    error_message = "deletion_window_in_days must be between 7 and 30."
  }
}

variable "environment" {
  description = "The environment (e.g., staging, production)."
  type        = string
}

variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "rotation_period_in_days" {
  description = "Rotation period in days."
  type        = number
  default     = 90

  validation {
    condition     = var.rotation_period_in_days >= 90 && var.rotation_period_in_days <= 2560
    error_message = "rotation_period_in_days must be between 90 and 2560."
  }
}
