variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "environment" {
  description = "The environment (e.g., staging, production)"
  type        = string
}

variable "aws_region" {
  description = "The AWS region"
  type        = string
}

variable "private_subnet_ids" {
  description = "A list of private subnet IDs"
  type        = list(string)
}

variable "lambda_sg_id" {
  description = "The ID of the security group for the Lambda function"
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
  default     = "512"
}

variable "update_project_health_metrics_task_cpu" {
  description = "The CPU for the update-project-health-metrics task"
  type        = string
  default     = "256"
}

variable "update_project_health_metrics_task_memory" {
  description = "The memory for the update-project-health-metrics task"
  type        = string
  default     = "512"
}

variable "update_project_health_scores_task_cpu" {
  description = "The CPU for the update-project-health-scores task"
  type        = string
  default     = "256"
}

variable "update_project_health_scores_task_memory" {
  description = "The memory for the update-project-health-scores task"
  type        = string
  default     = "512"
}

# One time tasks
variable "migrate_task_cpu" {
  description = "The CPU for the load-data task"
  type        = string
  default     = "256"
}

variable "migrate_task_memory" {
  description = "The memory for the load-data task"
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
# Environment Variables (temporary)
variable "django_algolia_application_id" {
  type        = string
  description = "Algolia application ID."
  default     = null
}

variable "django_allowed_hosts" {
  type        = string
  description = "Comma-separated list of allowed hosts for Django."
  default     = null
}

variable "django_db_host" {
  type        = string
  description = "Database host URL."
  default     = null
}

variable "django_db_name" {
  type        = string
  description = "Database name."
  default     = null
}

variable "django_db_user" {
  type        = string
  description = "Database user."
  default     = null
}

variable "django_db_port" {
  type        = string
  description = "Database port."
  default     = null
}

variable "django_redis_host" {
  type        = string
  description = "Redis host URL."
  default     = null
}

variable "django_algolia_write_api_key" {
  type        = string
  description = "Algolia write API key."
  sensitive   = true
  default     = null
}

variable "django_aws_access_key_id" {
  type        = string
  description = "AWS access key for Django."
  sensitive   = true
  default     = null
}

variable "django_aws_secret_access_key" {
  type        = string
  description = "AWS secret access key for Django."
  sensitive   = true
  default     = null
}

variable "django_configuration" {
  type        = string
  description = "Django Configuration"
  default     = null
}

variable "django_db_password" {
  type        = string
  description = "Database password."
  sensitive   = true
  default     = null
}

variable "django_open_ai_secret_key" {
  type        = string
  description = "OpenAI secret key."
  sensitive   = true
  default     = null
}

variable "django_redis_password" {
  type        = string
  description = "Redis password."
  sensitive   = true
  default     = null
}

variable "django_secret_key" {
  type        = string
  description = "Django secret key."
  sensitive   = true
  default     = null
}

variable "django_sentry_dsn" {
  type        = string
  description = "Sentry DSN for error tracking."
  sensitive   = true
  default     = null
}

variable "django_slack_bot_token" {
  type        = string
  description = "Slack bot token."
  sensitive   = true
  default     = null
}

variable "django_slack_signing_secret" {
  type        = string
  description = "Slack signing secret."
  sensitive   = true
  default     = null
}
