variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "db_password_arn" {
  description = "The SSM Parameter ARN of password of the database."
  type        = string
  sensitive   = true
}

variable "django_allowed_hosts" {
  description = "Django allowed hosts - hostname only, no protocol (e.g., nest.owasp.dev)."
  type        = string
}

variable "django_allowed_origins" {
  description = "The Django allowed CORS origins (comma-separated URLs with protocol)."
  type        = string
}

variable "django_aws_static_bucket_name" {
  description = "The name of the S3 bucket for Django static files."
  type        = string
}

variable "django_configuration" {
  description = "The name of the Django configuration to use (e.g., Staging, Production)."
  type        = string
}

variable "django_db_host" {
  description = "The hostname of the database."
  type        = string
}

variable "django_db_name" {
  description = "The name of the database."
  type        = string
}

variable "django_db_port" {
  description = "The port of the database."
  type        = string
}

variable "django_db_user" {
  description = "The user for the database."
  type        = string
}

variable "django_redis_host" {
  description = "The hostname of the Redis cache."
  type        = string
}

variable "django_redis_use_tls" {
  description = "Whether Redis connections should use TLS (required for ElastiCache with transit encryption)."
  type        = bool
  default     = true
}

variable "django_release_version" {
  description = "The Django release version."
  type        = string
}

variable "django_settings_module" {
  description = "The location of the Django settings module to use (e.g., settings.staging, settings.production)."
  type        = string
}

variable "enable_additional_parameters" {
  description = "Whether to create additional parameters (e.g. for production)."
  type        = bool
  default     = false
}

variable "environment" {
  description = "The environment (e.g., staging, production)."
  type        = string
}

variable "next_server_csrf_url" {
  description = "The server-side CSRF URL for Next.js SSR (e.g., https://nest.owasp.dev/csrf/)."
  type        = string
}

variable "next_server_graphql_url" {
  description = "The server-side GraphQL URL for Next.js SSR (e.g., https://nest.owasp.dev/graphql/)."
  type        = string
}

variable "nextauth_url" {
  description = "The NextAuth base URL (frontend URL with protocol)."
  type        = string
}

variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "redis_password_arn" {
  description = "The SSM Parameter ARN of password of the Redis cache."
  type        = string
  sensitive   = true
}

variable "slack_bot_token_suffix" {
  description = "The Suffix for the Slack bot token."
  type        = string
}
