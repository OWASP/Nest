variable "aws_region" {
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "us-east-1"
}

variable "availability_zones" {
  description = "A list of availability zones for the VPC"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "db_allocated_storage" {
  description = "The allocated storage for the RDS database in GB"
  type        = number
  default     = 20
}

variable "db_backup_retention_period" {
  description = "The number of days to retain backups for"
  type        = number
  default     = 7
}

variable "db_engine_version" {
  description = "The version of the PostgreSQL engine"
  type        = string
  default     = "16.10"
}

variable "db_instance_class" {
  description = "The instance class for the RDS database"
  type        = string
  default     = "db.t3.micro"
}

variable "db_name" {
  description = "The name of the RDS database"
  type        = string
  default     = "owasp_nest"
}

variable "db_password" {
  description = "The password for the RDS database"
  type        = string
  sensitive   = true
  default     = null
}

variable "db_port" {
  description = "The port for the RDS database"
  type        = number
  default     = 5432
}

variable "db_storage_type" {
  description = "The storage type for the RDS database"
  type        = string
  default     = "gp3"
}

variable "db_username" {
  description = "The username for the RDS database"
  type        = string
  default     = "owasp_nest_db_user"
}

variable "django_algolia_application_id" {
  type        = string
  description = "Algolia application ID."
  default     = null
}

variable "django_algolia_write_api_key" {
  type        = string
  description = "Algolia write API key."
  sensitive   = true
  default     = null
}

variable "django_allowed_hosts" {
  type        = string
  description = "Comma-separated list of allowed hosts for Django."
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

variable "django_db_password" {
  type        = string
  description = "Database password."
  sensitive   = true
  default     = null
}

variable "django_db_port" {
  type        = string
  description = "Database port."
  default     = null
}

variable "django_db_user" {
  type        = string
  description = "Database user."
  default     = null
}

variable "django_open_ai_secret_key" {
  type        = string
  description = "OpenAI secret key."
  sensitive   = true
  default     = null
}

variable "django_redis_host" {
  type        = string
  description = "Redis host URL."
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

variable "environment" {
  description = "The environment (e.g., staging, production)"
  type        = string
  default     = "staging"
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Environment must be either 'staging' or 'production'."
  }
}

variable "force_destroy_bucket" {
  description = "If true, deletes all objects from the bucket when the bucket is destroyed."
  type        = bool
  default     = false
}

variable "fixtures_s3_bucket" {
  description = "The name of the S3 bucket for fixtures"
  type        = string
  default     = "nest-fixtures"
}

variable "private_subnet_cidrs" {
  description = "A list of CIDR blocks for the private subnets"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
}

variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "nest"
}

variable "public_subnet_cidrs" {
  description = "A list of CIDR blocks for the public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "redis_auth_token" {
  description = "The auth token for Redis"
  type        = string
  sensitive   = true
  default     = null
}

variable "redis_engine_version" {
  description = "The version of the Redis engine"
  type        = string
  default     = "7.0"
}

variable "redis_node_type" {
  description = "The node type for the Redis cache"
  type        = string
  default     = "cache.t3.micro"
}

variable "redis_num_cache_nodes" {
  description = "The number of cache nodes in the Redis cluster"
  type        = number
  default     = 1
}

variable "redis_port" {
  description = "The port for the Redis cache"
  type        = number
  default     = 6379
}

variable "vpc_cidr" {
  description = "The CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "zappa_s3_bucket" {
  description = "The name of the S3 bucket for Zappa deployments"
  type        = string
  default     = "owasp-nest-zappa-deployments"
}
