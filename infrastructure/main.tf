terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

locals {
  common_tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
    Project     = var.project_name
  }
  django_environment_variables = {
    DJANGO_ALGOLIA_APPLICATION_ID = var.django_algolia_application_id
    DJANGO_ALGOLIA_WRITE_API_KEY  = var.django_algolia_write_api_key
    DJANGO_ALLOWED_HOSTS          = var.django_allowed_hosts
    DJANGO_AWS_ACCESS_KEY_ID      = var.django_aws_access_key_id
    DJANGO_AWS_SECRET_ACCESS_KEY  = var.django_aws_secret_access_key
    DJANGO_CONFIGURATION          = var.django_configuration
    DJANGO_DB_HOST                = var.django_db_host
    DJANGO_DB_NAME                = var.django_db_name
    DJANGO_DB_USER                = var.django_db_user
    DJANGO_DB_PORT                = var.django_db_port
    DJANGO_DB_PASSWORD            = var.django_db_password
    DJANGO_OPEN_AI_SECRET_KEY     = var.django_open_ai_secret_key
    DJANGO_REDIS_HOST             = var.django_redis_host
    DJANGO_REDIS_PASSWORD         = var.django_redis_password
    DJANGO_SECRET_KEY             = var.django_secret_key
    DJANGO_SENTRY_DSN             = var.django_sentry_dsn
    DJANGO_SLACK_BOT_TOKEN        = var.django_slack_bot_token
    DJANGO_SLACK_SIGNING_SECRET   = var.django_slack_signing_secret
  }
}

module "networking" {
  source = "./modules/networking"

  availability_zones   = var.availability_zones
  common_tags          = local.common_tags
  environment          = var.environment
  private_subnet_cidrs = var.private_subnet_cidrs
  project_name         = var.project_name
  public_subnet_cidrs  = var.public_subnet_cidrs
  vpc_cidr             = var.vpc_cidr
}

module "security" {
  source = "./modules/security"

  common_tags  = local.common_tags
  db_port      = var.db_port
  environment  = var.environment
  project_name = var.project_name
  redis_port   = var.redis_port
  vpc_id       = module.networking.vpc_id
}

module "storage" {
  source = "./modules/storage"

  common_tags          = local.common_tags
  environment          = var.environment
  force_destroy_bucket = var.force_destroy_bucket
  project_name         = var.project_name
  zappa_s3_bucket      = var.zappa_s3_bucket
}

module "database" {
  source = "./modules/database"

  common_tags                = local.common_tags
  db_allocated_storage       = var.db_allocated_storage
  db_backup_retention_period = var.db_backup_retention_period
  db_engine_version          = var.db_engine_version
  db_instance_class          = var.db_instance_class
  db_name                    = var.db_name
  db_password                = var.db_password
  db_storage_type            = var.db_storage_type
  db_subnet_ids              = module.networking.private_subnet_ids
  db_username                = var.db_username
  environment                = var.environment
  project_name               = var.project_name
  proxy_security_group_ids   = [module.security.rds_proxy_sg_id]
  security_group_ids         = [module.security.rds_sg_id]
}

module "cache" {
  source = "./modules/cache"

  common_tags           = local.common_tags
  environment           = var.environment
  project_name          = var.project_name
  redis_auth_token      = var.redis_auth_token
  redis_engine_version  = var.redis_engine_version
  redis_node_type       = var.redis_node_type
  redis_num_cache_nodes = var.redis_num_cache_nodes
  redis_port            = var.redis_port
  security_group_ids    = [module.security.redis_sg_id]
  subnet_ids            = module.networking.private_subnet_ids
}

module "ecs" {
  source = "./modules/ecs"

  aws_region                   = var.aws_region
  common_tags                  = local.common_tags
  django_environment_variables = local.django_environment_variables
  environment                  = var.environment
  lambda_sg_id                 = module.security.lambda_sg_id
  private_subnet_ids           = module.networking.private_subnet_ids
  project_name                 = var.project_name
}
