variable "aws_region" {
  description = "The AWS region"
  type        = string
}

variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "container_parameters_arns" {
  description = "Map of environment variable names to the ARNs of all SSM parameters."
  type        = map(string)
  default     = {}
}

variable "ecs_sg_id" {
  description = "The ID of the security group for the ECS tasks"
  type        = string
}

variable "environment" {
  description = "The environment (e.g., staging, production)"
  type        = string
}

variable "fixtures_read_only_policy_arn" {
  description = "The ARN of the fixtures read-only IAM policy"
  type        = string
}

variable "fixtures_bucket_name" {
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
  default     = "1024"
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
  default     = "1024"
}

variable "update_project_health_metrics_task_cpu" {
  description = "The CPU for the update-project-health-metrics task"
  type        = string
  default     = "256"
}

variable "update_project_health_metrics_task_memory" {
  description = "The memory for the update-project-health-metrics task"
  type        = string
  default     = "1024"
}

variable "update_project_health_scores_task_cpu" {
  description = "The CPU for the update-project-health-scores task"
  type        = string
  default     = "256"
}

variable "update_project_health_scores_task_memory" {
  description = "The memory for the update-project-health-scores task"
  type        = string
  default     = "1024"
}
