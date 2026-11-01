variable "auto_scaling_cpu_target" {
  description = "Target average CPU utilization percentage for auto scaling."
  type        = number
  default     = 70

  validation {
    condition     = var.auto_scaling_cpu_target >= 1 && var.auto_scaling_cpu_target <= 100
    error_message = "auto_scaling_cpu_target must be between 1 and 100."
  }
}

variable "auto_scaling_scale_in_cooldown" {
  description = "Cooldown period in seconds after a scale-in activity."
  type        = number
  default     = 300

  validation {
    condition     = var.auto_scaling_scale_in_cooldown >= 0
    error_message = "auto_scaling_scale_in_cooldown must be >= 0."
  }
}

variable "auto_scaling_scale_out_cooldown" {
  description = "Cooldown period in seconds after a scale-out activity."
  type        = number
  default     = 60

  validation {
    condition     = var.auto_scaling_scale_out_cooldown >= 0
    error_message = "auto_scaling_scale_out_cooldown must be >= 0."
  }
}

variable "aws_region" {
  description = "The AWS region."
  type        = string
}

variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "command" {
  description = "The command to run in the container. If null, the container's default CMD is used."
  type        = list(string)
  default     = null
}

variable "container_cpu" {
  description = "The CPU units for the container (1024 = 1 vCPU)."
  type        = number
  default     = 512
}

variable "container_memory" {
  description = "The memory for the container in MiB."
  type        = number
  default     = 1024
}

variable "container_port" {
  description = "The port the container listens on."
  type        = number
}

variable "container_stop_timeout" {
  description = "Seconds to allow the container to stop gracefully. Null uses the ECS default."
  type        = number
  default     = null

  validation {
    condition     = var.container_stop_timeout == null ? true : var.container_stop_timeout >= 2 && var.container_stop_timeout <= 120 && floor(var.container_stop_timeout) == var.container_stop_timeout
    error_message = "container_stop_timeout must be a whole number between 2 and 120 seconds."
  }
}

variable "desired_count" {
  description = "The desired number of tasks."
  type        = number
  default     = 2
}

variable "enable_auto_scaling" {
  description = "Whether to enable auto scaling for the service."
  type        = bool
  default     = false
}

variable "environment" {
  description = "The environment name (e.g., staging, production)."
  type        = string
}

variable "environment_variables" {
  description = "Non-secret container environment variables. Names must not overlap parameters_arns."
  type        = map(string)
  default     = {}

  validation {
    condition     = length(setintersection(keys(var.environment_variables), keys(var.parameters_arns))) == 0
    error_message = "environment_variables and parameters_arns must not contain the same names."
  }
}

variable "force_new_deployment" {
  description = "Whether to force a new deployment on each apply."
  type        = bool
  default     = false
}

variable "health_check_command" {
  description = "Optional ECS health check command. Null keeps the default wget probe."
  type        = list(string)
  default     = null

  validation {
    condition     = var.health_check_command == null ? true : try(length(var.health_check_command) >= 2 && contains(["CMD", "CMD-SHELL"], var.health_check_command[0]), false)
    error_message = "health_check_command must start with CMD or CMD-SHELL and include a command."
  }
}

variable "health_check_path" {
  description = "The path for the ECS container health checks."
  type        = string
  default     = "/"

  validation {
    condition     = startswith(var.health_check_path, "/")
    error_message = "health_check_path must start with '/'."
  }
}

variable "image_tag" {
  description = "The Docker image tag."
  type        = string
}

variable "kms_key_arn" {
  description = "The ARN of the KMS key for log encryption."
  type        = string
}

variable "log_retention_in_days" {
  description = "The CloudWatch log retention in days."
  type        = number
  default     = 30
}

variable "max_count" {
  description = "The maximum number of tasks for auto scaling."
  type        = number
  default     = 6

  validation {
    condition     = !var.enable_auto_scaling || var.desired_count <= var.max_count
    error_message = "When auto scaling is enabled, desired_count must be <= max_count."
  }
}

variable "min_count" {
  description = "The minimum number of tasks for auto scaling."
  type        = number
  default     = 2

  validation {
    condition     = !var.enable_auto_scaling || var.min_count <= var.desired_count
    error_message = "When auto scaling is enabled, min_count must be <= desired_count."
  }
}

variable "parameters_arns" {
  description = "Map of environment variable names to the ARNs of SSM parameters."
  type        = map(string)
  default     = {}
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for ECS tasks."
  type        = list(string)

  validation {
    condition     = length(var.private_subnet_ids) > 0
    error_message = "private_subnet_ids must contain at least one subnet."
  }
}

variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "security_group_id" {
  description = "The ID of the security group for the service."
  type        = string
}

variable "service_name" {
  description = "The name of the service (e.g., backend, frontend)."
  type        = string
}

variable "target_group_arn" {
  description = "The ARN of the ALB target group."
  type        = string
}

variable "task_role_policy_arns" {
  description = "A list of additional IAM policy ARNs to attach to the ECS task role."
  type        = list(string)
  default     = []
}

variable "use_fargate_spot" {
  description = "Whether to use Fargate Spot capacity provider."
  type        = bool
  default     = false
}
