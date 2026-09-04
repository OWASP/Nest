variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "db_credentials_secret_arn" {
  description = "The Secrets Manager ARN containing the database credentials."
  type        = string
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

variable "kms_key_arn" {
  description = "The KMS key ARN used to encrypt runtime secrets"
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

variable "redis_password_secret_arn" {
  description = "The Secrets Manager ARN containing the Redis password."
  type        = string
}

variable "runtime_secrets_mode" {
  description = "Runtime secret migration phase: 'prepare' retains SSM injection, while 'complete' uses Secrets Manager."
  type        = string

  validation {
    condition = contains(
      ["prepare", "complete"],
      var.runtime_secrets_mode,
    )
    error_message = "runtime_secrets_mode must be either prepare or complete."
  }
}
variable "secret_recovery_window_in_days" {
  description = "The number of days Secrets Manager waits before deleting a secret."
  type        = number
  default     = 7

  # A value of 0 maps to ForceDeleteWithoutRecovery and should only be used for
  # ephemeral/test environments. Staging and production should use 7-30 days.
  validation {
    condition = (
      var.secret_recovery_window_in_days == 0 ||
      (
        var.secret_recovery_window_in_days >= 7 &&
        var.secret_recovery_window_in_days <= 30
      )
    )
    error_message = "secret_recovery_window_in_days must be 0 (immediate deletion) or between 7 and 30."
  }

}


variable "slack_bot_token_suffix" {
  description = "The Suffix for the Slack bot token."
  type        = string
}
