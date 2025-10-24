variable "aws_region" {
  description = "The AWS region"
  type        = string
}

variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "django_environment_variables" {
  description = "A map of environment variables for the Django container."
  type        = map(string)
  default     = {}
  sensitive   = true
}

variable "environment" {
  description = "The environment (e.g., staging, production)"
  type        = string
}

variable "fixtures_read_only_policy_arn" {
  description = "The ARN of the fixtures read-only IAM policy"
  type        = string
}

variable "fixtures_s3_bucket" {
  description = "The name of the S3 bucket for fixtures"
  type        = string
}

variable "index_data_task_cpu" {
  description = "The CPU for the index-data task"
  type        = string
  default     = "256"
}

variable "index_data_task_memory" {
  description = "The memory for the index-data task"
  type        = string
  default     = "2048"
}

variable "lambda_sg_id" {
  description = "The ID of the security group for the Lambda function"
  type        = string
}

variable "load_data_task_cpu" {
  description = "The CPU for the load-data task"
  type        = string
  default     = "256"
}

variable "load_data_task_memory" {
  description = "The memory for the load-data task"
  type        = string
  default     = "2048"
}

variable "migrate_task_cpu" {
  description = "The CPU for the migrate task"
  type        = string
  default     = "256"
}

variable "migrate_task_memory" {
  description = "The memory for the migrate task"
  type        = string
  default     = "2048"
}

variable "private_subnet_ids" {
  description = "A list of private subnet IDs"
  type        = list(string)
}

variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "sync_data_task_cpu" {
  description = "The CPU for the sync-data task"
  type        = string
  default     = "256"
}

variable "sync_data_task_memory" {
  description = "The memory for the sync-data task"
  type        = string
  default     = "2048"
}

variable "update_project_health_metrics_task_cpu" {
  description = "The CPU for the update-project-health-metrics task"
  type        = string
  default     = "256"
}

variable "update_project_health_metrics_task_memory" {
  description = "The memory for the update-project-health-metrics task"
  type        = string
  default     = "2048"
}

variable "update_project_health_scores_task_cpu" {
  description = "The CPU for the update-project-health-scores task"
  type        = string
  default     = "256"
}

variable "update_project_health_scores_task_memory" {
  description = "The memory for the update-project-health-scores task"
  type        = string
  default     = "2048"
}
