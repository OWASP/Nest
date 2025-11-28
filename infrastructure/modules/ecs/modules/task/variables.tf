variable "aws_region" {
  description = "The AWS region for the CloudWatch logs."
  type        = string
}

variable "command" {
  description = "The command to run in the container."
  type        = list(string)
}

variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "container_parameters_arns" {
  description = "A Map of environment variable names to the ARNs of all SSM parameters."
  type        = map(string)
  default     = {}
}

variable "cpu" {
  description = "The CPU units to allocate for the task."
  type        = string
}

variable "ecs_cluster_arn" {
  description = "The ARN of the ECS cluster."
  type        = string
}

variable "ecs_tasks_execution_role_arn" {
  description = "The ARN of the ECS task execution role."
  type        = string
}

variable "environment" {
  description = "The environment (e.g., staging, production)."
  type        = string
}

variable "event_bridge_role_arn" {
  description = "The ARN of the EventBridge role to trigger the task. Only required for scheduled tasks."
  type        = string
  default     = null
}

variable "image_url" {
  description = "The URL of the ECR image to run."
  type        = string
}

variable "log_retention_in_days" {
  description = "The number of days to retain log events."
  type        = number
  default     = 90
}

variable "memory" {
  description = "The memory (in MiB) to allocate for the task."
  type        = string
}

variable "private_subnet_ids" {
  description = "A list of private subnet IDs for the task."
  type        = list(string)
}

variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "schedule_expression" {
  description = "The cron expression for the schedule. If null, the task is not scheduled."
  type        = string
  default     = null
}

variable "security_group_ids" {
  description = "A list of security group IDs to associate with the task."
  type        = list(string)
}

variable "task_name" {
  description = "The unique name of the task."
  type        = string
}

variable "task_role_arn" {
  description = "The ARN of the IAM role for the task."
  type        = string
  default     = null
}
