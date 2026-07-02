terraform {
  required_version = "~> 1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.36.0"
    }
  }
}

provider "aws" {
  region = "us-east-2"
}

variable "runtime_secrets_mode" {
  type    = string
  default = "prepare"

  validation {
    condition     = contains(["prepare", "complete"], var.runtime_secrets_mode)
    error_message = "runtime_secrets_mode must be either prepare or complete."
  }
}

locals {
  tags = {
    Environment = "localstack"
    Project     = "nest"
  }
}

resource "aws_kms_key" "main" {
  description = "LocalStack runtime-secret test key"
}

resource "aws_secretsmanager_secret" "db" {
  name                    = "nest-localstack-db-credentials"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "db" {
  secret_id = aws_secretsmanager_secret.db.id
  secret_string = jsonencode({
    username = "nest"
    password = "local-db-password"
  })
}

resource "aws_secretsmanager_secret" "redis" {
  name                    = "/nest/localstack/DJANGO_REDIS_PASSWORD"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "redis" {
  secret_id     = aws_secretsmanager_secret.redis.id
  secret_string = "local-redis-password"
}

resource "aws_ssm_parameter" "db_password" {
  count = var.runtime_secrets_mode == "prepare" ? 1 : 0

  name  = "/nest/localstack/DJANGO_DB_PASSWORD"
  type  = "SecureString"
  value = "local-db-password"
}

resource "aws_ssm_parameter" "redis_password" {
  count = var.runtime_secrets_mode == "prepare" ? 1 : 0

  name  = "/nest/localstack/DJANGO_REDIS_PASSWORD"
  type  = "SecureString"
  value = "local-redis-password"
}

module "parameters" {
  source = "../modules/parameters"

  common_tags                    = local.tags
  db_credentials_secret_arn      = aws_secretsmanager_secret.db.arn
  db_password_arn                = try(aws_ssm_parameter.db_password[0].arn, null)
  django_allowed_hosts           = "localhost"
  django_allowed_origins         = "http://localhost"
  django_aws_static_bucket_name  = "nest-localstack-static"
  django_configuration           = "Local"
  django_db_host                 = "localhost"
  django_db_name                 = "nest"
  django_db_port                 = "5432"
  django_db_user                 = "nest"
  django_redis_host              = "localhost"
  django_redis_use_tls           = false
  django_release_version         = "local"
  django_settings_module         = "settings.local"
  enable_additional_parameters   = false
  environment                    = "localstack"
  kms_key_arn                    = aws_kms_key.main.arn
  next_server_csrf_url           = "http://localhost/csrf/"
  next_server_graphql_url        = "http://localhost/graphql/"
  nextauth_url                   = "http://localhost"
  project_name                   = "nest"
  redis_password_arn             = try(aws_ssm_parameter.redis_password[0].arn, null)
  redis_password_secret_arn      = aws_secretsmanager_secret.redis.arn
  runtime_secrets_mode           = var.runtime_secrets_mode
  secret_recovery_window_in_days = 0
  slack_bot_token_suffix         = "T04T40NHX"
}

resource "aws_iam_role" "ecs_execution" {
  name = "nest-localstack-runtime-secrets-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "runtime_secrets" {
  name = "nest-localstack-runtime-secrets"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = ["secretsmanager:GetSecretValue"]
        Effect   = "Allow"
        Resource = module.parameters.secretsmanager_secret_arns
      },
      {
        Action   = ["kms:Decrypt"]
        Effect   = "Allow"
        Resource = aws_kms_key.main.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "runtime_secrets" {
  policy_arn = aws_iam_policy.runtime_secrets.arn
  role       = aws_iam_role.ecs_execution.name
}

resource "aws_ecs_task_definition" "django" {
  container_definitions = jsonencode([{
    essential = true
    image     = "public.ecr.aws/docker/library/busybox:latest"
    name      = "backend"
    secrets = [for name, valueFrom in module.parameters.django_container_secrets : {
      name      = name
      valueFrom = valueFrom
    }]
  }])
  cpu                      = "256"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  family                   = "nest-localstack-runtime-secrets"
  memory                   = "512"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
}

output "django_value_from" {
  description = "Django environment variable names mapped to ECS valueFrom references."
  sensitive   = true
  value       = module.parameters.django_container_secrets
}

output "frontend_value_from" {
  description = "Frontend environment variable names mapped to ECS valueFrom references."
  sensitive   = true
  value       = module.parameters.frontend_container_secrets
}

output "execution_policy_arn" {
  description = "ARN of the fixture execution-role policy."
  value       = aws_iam_policy.runtime_secrets.arn
}

output "kms_key_arn" {
  description = "ARN of the fixture KMS key."
  value       = aws_kms_key.main.arn
}

output "secretsmanager_secret_arns" {
  description = "Bare Secrets Manager ARNs passed to the execution-role policy."
  value       = module.parameters.secretsmanager_secret_arns
}

output "task_definition_arn" {
  description = "ARN of the fixture Django ECS task definition."
  value       = aws_ecs_task_definition.django.arn
}
