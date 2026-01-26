variable "aws_region" {
  description = "The AWS region for resources."
  type        = string
}

variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "container_cpu" {
  description = "The CPU units for the frontend container (1024 = 1 vCPU)."
  type        = number
  default     = 512
}

variable "container_memory" {
  description = "The memory for the frontend container in MB."
  type        = number
  default     = 1024
}

variable "desired_count" {
  description = "The desired number of frontend tasks."
  type        = number
  default     = 2
}

variable "enable_auto_scaling" {
  description = "Whether to enable auto scaling for the frontend."
  type        = bool
  default     = false
}

variable "environment" {
  description = "The environment name (e.g., staging, production)."
  type        = string
}

variable "frontend_parameters_arns" {
  description = "A map of environment variable names to SSM parameter ARNs."
  type        = map(string)
}

variable "frontend_sg_id" {
  description = "The security group ID for the frontend ECS tasks."
  type        = string
}

variable "image_tag" {
  description = "The Docker image tag for the frontend."
  type        = string
  default     = "latest"
}

variable "log_retention_in_days" {
  description = "The CloudWatch log retention in days."
  type        = number
  default     = 7
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

variable "private_subnet_ids" {
  description = "A list of private subnet IDs for ECS tasks."
  type        = list(string)
}

variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "target_group_arn" {
  description = "The ARN of the ALB target group for the frontend."
  type        = string
}

variable "use_fargate_spot" {
  description = "Whether to use Fargate Spot capacity provider for frontend tasks."
  type        = bool
  default     = false
}
