terraform {
  required_version = "~> 1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.36.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.8.0"
    }
  }
}

resource "aws_ssm_parameter" "django_algolia_application_id" {
  description = "Algolia Application ID."
  name        = "/${var.project_name}/${var.environment}/DJANGO_ALGOLIA_APPLICATION_ID"
  tags        = var.common_tags
  type        = "SecureString"
  value       = "to-be-set-in-aws-console"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "django_algolia_write_api_key" {
  description = "Algolia Write API Key."
  name        = "/${var.project_name}/${var.environment}/DJANGO_ALGOLIA_WRITE_API_KEY"
  tags        = var.common_tags
  type        = "SecureString"
  value       = "to-be-set-in-aws-console"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "django_allowed_hosts" {
  description = "Django allowed hosts - hostname only, no protocol (e.g., nest.owasp.dev)."
  name        = "/${var.project_name}/${var.environment}/DJANGO_ALLOWED_HOSTS"
  tags        = var.common_tags
  type        = "String"
  value       = var.django_allowed_hosts

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "django_allowed_origins" {
  description = "Django allowed CORS origins - full URL with protocol (e.g., https://nest.owasp.dev)."
  name        = "/${var.project_name}/${var.environment}/DJANGO_ALLOWED_ORIGINS"
  tags        = var.common_tags
  type        = "String"
  value       = var.django_allowed_origins

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "django_aws_storage_bucket_name" {
  description = "The S3 bucket name for Django static files."
  name        = "/${var.project_name}/${var.environment}/DJANGO_AWS_STORAGE_BUCKET_NAME"
  tags        = var.common_tags
  type        = "String"
  value       = var.django_aws_static_bucket_name
}

resource "aws_ssm_parameter" "django_configuration" {
  description = "The name of the Django configuration to use (e.g., Staging, Production)."
  name        = "/${var.project_name}/${var.environment}/DJANGO_CONFIGURATION"
  tags        = var.common_tags
  type        = "String"
  value       = var.django_configuration

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "django_db_host" {
  description = "The hostname of the database."
  name        = "/${var.project_name}/${var.environment}/DJANGO_DB_HOST"
  tags        = var.common_tags
  type        = "String"
  value       = var.django_db_host
}

resource "aws_ssm_parameter" "django_db_name" {
  description = "The name of the database."
  name        = "/${var.project_name}/${var.environment}/DJANGO_DB_NAME"
  tags        = var.common_tags
  type        = "String"
  value       = var.django_db_name
}

resource "aws_ssm_parameter" "django_db_port" {
  description = "The port of the database."
  name        = "/${var.project_name}/${var.environment}/DJANGO_DB_PORT"
  tags        = var.common_tags
  type        = "String"
  value       = var.django_db_port
}

resource "aws_ssm_parameter" "django_db_user" {
  description = "The user for the database."
  name        = "/${var.project_name}/${var.environment}/DJANGO_DB_USER"
  tags        = var.common_tags
  type        = "String"
  value       = var.django_db_user
}

resource "aws_ssm_parameter" "django_github_app_id" {
  count       = var.enable_additional_parameters ? 1 : 0
  description = "Django GitHub App ID."
  name        = "/${var.project_name}/${var.environment}/DJANGO_GITHUB_APP_ID"
  tags        = var.common_tags
  type        = "String"
  value       = "to-be-set-in-aws-console"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "django_github_app_installation_id" {
  count       = var.enable_additional_parameters ? 1 : 0
  description = "Django GitHub App installation ID."
  name        = "/${var.project_name}/${var.environment}/DJANGO_GITHUB_APP_INSTALLATION_ID"
  tags        = var.common_tags
  type        = "String"
  value       = "to-be-set-in-aws-console"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "django_release_version" {
  count       = var.enable_additional_parameters ? 1 : 0
  description = "Django Release version."
  name        = "/${var.project_name}/${var.environment}/DJANGO_RELEASE_VERSION"
  tags        = var.common_tags
  type        = "String"
  value       = var.django_release_version
}

resource "aws_ssm_parameter" "django_open_ai_secret_key" {
  description = "OpenAI Secret Key."
  name        = "/${var.project_name}/${var.environment}/DJANGO_OPEN_AI_SECRET_KEY"
  tags        = var.common_tags
  type        = "SecureString"
  value       = "to-be-set-in-aws-console"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "django_redis_host" {
  description = "The hostname of the Redis cache."
  name        = "/${var.project_name}/${var.environment}/DJANGO_REDIS_HOST"
  tags        = var.common_tags
  type        = "String"
  value       = var.django_redis_host
}

resource "aws_ssm_parameter" "django_redis_use_tls" {
  description = "Whether Redis connections should use TLS (required for ElastiCache with transit encryption)."
  name        = "/${var.project_name}/${var.environment}/DJANGO_REDIS_USE_TLS"
  tags        = var.common_tags
  type        = "String"
  value       = tostring(var.django_redis_use_tls)
}

resource "aws_ssm_parameter" "django_secret_key" {
  description = "Django Secret Key generated by Terraform."
  name        = "/${var.project_name}/${var.environment}/DJANGO_SECRET_KEY"
  tags        = var.common_tags
  type        = "SecureString"
  value       = random_string.django_secret_key.result
}

resource "aws_ssm_parameter" "django_settings_module" {
  description = "The location of the Django settings module to use (e.g., settings.staging, settings.production)."
  name        = "/${var.project_name}/${var.environment}/DJANGO_SETTINGS_MODULE"
  tags        = var.common_tags
  type        = "String"
  value       = var.django_settings_module

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "django_sentry_dsn" {
  description = "The DSN for the Sentry project."
  name        = "/${var.project_name}/${var.environment}/DJANGO_SENTRY_DSN"
  tags        = var.common_tags
  type        = "SecureString"
  value       = "to-be-set-in-aws-console"

  lifecycle {
    ignore_changes = [value]
  }
}


resource "aws_ssm_parameter" "django_slack_bot_token" {
  description = "The bot token for the Slack integration."
  name        = "/${var.project_name}/${var.environment}/DJANGO_SLACK_BOT_TOKEN"
  tags        = var.common_tags
  type        = "SecureString"
  value       = "to-be-set-in-aws-console"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "django_slack_signing_secret" {
  description = "The signing secret for the Slack integration."
  name        = "/${var.project_name}/${var.environment}/DJANGO_SLACK_SIGNING_SECRET"
  tags        = var.common_tags
  type        = "SecureString"
  value       = "to-be-set-in-aws-console"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "github_token" {
  description = "GitHub Personal Access Token for GitHub API authentication."
  name        = "/${var.project_name}/${var.environment}/GITHUB_TOKEN"
  tags        = var.common_tags
  type        = "SecureString"
  value       = "to-be-set-in-aws-console"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "nest_github_app_private_key" {
  count       = var.enable_additional_parameters ? 1 : 0
  description = "GitHub App private key."
  name        = "/${var.project_name}/${var.environment}/NEST_GITHUB_APP_PRIVATE_KEY"
  tags        = var.common_tags
  type        = "SecureString"
  value       = "to-be-set-in-aws-console"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "next_server_csrf_url" {
  description = "The server-side CSRF URL for Next.js SSR."
  name        = "/${var.project_name}/${var.environment}/NEXT_SERVER_CSRF_URL"
  tags        = var.common_tags
  type        = "String"
  value       = var.next_server_csrf_url
}

resource "aws_ssm_parameter" "next_server_disable_ssr" {
  description = "A flag to disable server-side rendering."
  name        = "/${var.project_name}/${var.environment}/NEXT_SERVER_DISABLE_SSR"
  tags        = var.common_tags
  type        = "String"
  value       = "false"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "next_server_github_client_id" {
  description = "The GitHub OAuth client ID for NextAuth."
  name        = "/${var.project_name}/${var.environment}/NEXT_SERVER_GITHUB_CLIENT_ID"
  tags        = var.common_tags
  type        = "String"
  value       = "to-be-set-in-aws-console"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "next_server_github_client_secret" {
  description = "The GitHub OAuth client secret for NextAuth."
  name        = "/${var.project_name}/${var.environment}/NEXT_SERVER_GITHUB_CLIENT_SECRET"
  tags        = var.common_tags
  type        = "SecureString"
  value       = "to-be-set-in-aws-console"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "next_server_graphql_url" {
  description = "The server-side GraphQL URL for Next.js SSR."
  name        = "/${var.project_name}/${var.environment}/NEXT_SERVER_GRAPHQL_URL"
  tags        = var.common_tags
  type        = "String"
  value       = var.next_server_graphql_url
}

resource "aws_ssm_parameter" "nextauth_secret" {
  description = "NextAuth secret key generated by Terraform."
  name        = "/${var.project_name}/${var.environment}/NEXTAUTH_SECRET"
  tags        = var.common_tags
  type        = "SecureString"
  value       = random_string.nextauth_secret.result
}

resource "aws_ssm_parameter" "nextauth_url" {
  description = "NextAuth base URL - full URL with protocol (e.g., https://nest.owasp.dev)."
  name        = "/${var.project_name}/${var.environment}/NEXTAUTH_URL"
  tags        = var.common_tags
  type        = "String"
  value       = var.nextauth_url

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "slack_bot_token" {
  count       = var.enable_additional_parameters ? 1 : 0
  description = "Slack bot token."
  name        = "/${var.project_name}/${var.environment}/SLACK_BOT_TOKEN_${var.slack_bot_token_suffix}"
  tags        = var.common_tags
  type        = "SecureString"
  value       = "to-be-set-in-aws-console"

  lifecycle {
    ignore_changes = [value]
  }
}


resource "random_string" "django_secret_key" {
  length  = 50
  special = true
}

resource "random_string" "nextauth_secret" {
  length  = 32
  special = true
}
