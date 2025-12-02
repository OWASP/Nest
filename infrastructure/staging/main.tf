terraform {
  required_version = "1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.22.0"
    }
  }
}

locals {
  common_tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
    Project     = var.project_name
  }
}

module "cache" {
  source = "../modules/cache"

  common_tags           = local.common_tags
  environment           = var.environment
  project_name          = var.project_name
  redis_engine_version  = var.redis_engine_version
  redis_node_type       = var.redis_node_type
  redis_num_cache_nodes = var.redis_num_cache_nodes
  redis_port            = var.redis_port
  security_group_ids    = [module.security.redis_sg_id]
  subnet_ids            = module.networking.private_subnet_ids
}

module "database" {
  source = "../modules/database"

  common_tags                = local.common_tags
  create_rds_proxy           = var.create_rds_proxy
  db_allocated_storage       = var.db_allocated_storage
  db_backup_retention_period = var.db_backup_retention_period
  db_engine_version          = var.db_engine_version
  db_instance_class          = var.db_instance_class
  db_name                    = var.db_name
  db_password                = var.db_password
  db_storage_type            = var.db_storage_type
  db_subnet_ids              = module.networking.private_subnet_ids
  db_user                    = var.db_user
  environment                = var.environment
  project_name               = var.project_name
  proxy_security_group_ids   = [module.security.rds_proxy_sg_id]
  security_group_ids         = [module.security.rds_sg_id]
}

module "ecs" {
  source = "../modules/ecs"

  aws_region                    = var.aws_region
  common_tags                   = local.common_tags
  container_parameters_arns     = module.parameters.ssm_parameter_arns
  ecs_sg_id                     = module.security.ecs_sg_id
  environment                   = var.environment
  fixtures_read_only_policy_arn = module.storage.fixtures_read_only_policy_arn
  fixtures_bucket_name          = module.storage.fixtures_s3_bucket_name
  private_subnet_ids            = module.networking.private_subnet_ids
  project_name                  = var.project_name
}

module "networking" {
  source = "../modules/networking"

  aws_region           = var.aws_region
  availability_zones   = var.availability_zones
  common_tags          = local.common_tags
  environment          = var.environment
  private_subnet_cidrs = var.private_subnet_cidrs
  project_name         = var.project_name
  public_subnet_cidrs  = var.public_subnet_cidrs
  vpc_cidr             = var.vpc_cidr
}

module "parameters" {
  source = "../modules/parameters"

  common_tags    = local.common_tags
  db_host        = module.database.db_proxy_endpoint
  db_name        = var.db_name
  db_password    = module.database.db_password
  db_port        = var.db_port
  db_user        = var.db_user
  environment    = var.environment
  project_name   = var.project_name
  redis_host     = module.cache.redis_primary_endpoint
  redis_password = module.cache.redis_auth_token
}

module "security" {
  source = "../modules/security"

  common_tags        = local.common_tags
  create_rds_proxy   = var.create_rds_proxy
  db_port            = var.db_port
  environment        = var.environment
  project_name       = var.project_name
  redis_port         = var.redis_port
  vpc_endpoint_sg_id = module.networking.vpc_endpoint_security_group_id
  vpc_id             = module.networking.vpc_id
}

module "storage" {
  source = "../modules/storage"

  common_tags          = local.common_tags
  environment          = var.environment
  fixtures_bucket_name = var.fixtures_bucket_name
  project_name         = var.project_name
  zappa_bucket_name    = var.zappa_bucket_name
}
