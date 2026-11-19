variable "task_context" {
  description = "Shared image, container configuration, cluster, roles and task size from the parent service."
  sensitive   = true
  type = object({
    cluster_arn          = string
    execution_role_arn   = string
    task_role_arn        = string
    cpu                  = number
    memory               = number
    container_definition = any
  })
}

variable "name_prefix" {
  description = "Prefix for the worker task family and service name."
  type        = string
}

variable "container_name" {
  description = "Worker container name."
  type        = string
}

variable "command" {
  description = "Command executed by the worker."
  type        = list(string)

  validation {
    condition     = try(length(var.command) > 0 && trimspace(var.command[0]) != "", false)
    error_message = "command must contain a non-blank executable."
  }
}

variable "health_check_command" {
  description = "ECS worker health check command."
  type        = list(string)

  validation {
    condition     = try(length(var.health_check_command) >= 2 && contains(["CMD", "CMD-SHELL"], var.health_check_command[0]) && trimspace(var.health_check_command[1]) != "", false)
    error_message = "health_check_command must start with CMD or CMD-SHELL and include a non-blank command."
  }
}

variable "desired_count" {
  description = "Desired number of worker tasks."
  type        = number
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for worker tasks."
  type        = list(string)

  validation {
    condition     = length(var.private_subnet_ids) > 0
    error_message = "private_subnet_ids must contain at least one subnet."
  }
}

variable "security_group_id" {
  description = "Security group ID for worker tasks."
  type        = string
}

variable "common_tags" {
  description = "Tags applied to worker resources."
  type        = map(string)
  default     = {}
}

variable "force_new_deployment" {
  description = "Whether to force a new deployment on each apply."
  type        = bool
  default     = false
}

variable "use_fargate_spot" {
  description = "Whether to use Fargate Spot capacity."
  type        = bool
  default     = false
}
