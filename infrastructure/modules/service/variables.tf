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

variable "force_new_deployment" {
  description = "Whether to force a new deployment on each apply."
  type        = bool
  default     = false
}

variable "image_tag" {
  description = "The Docker image tag."
  type        = string
  default     = "latest"
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
  description = "A list of private subnet IDs for the service."
  type        = list(string)
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

variable "use_fargate_spot" {
  description = "Whether to use Fargate Spot capacity provider."
  type        = bool
  default     = false
}
