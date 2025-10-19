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

module "networking" {
  source = "./modules/networking"

  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones   = var.availability_zones
  project_name         = var.project_name
  environment          = var.environment
}

module "security" {
  source = "./modules/security"

  vpc_id       = module.networking.vpc_id
  db_port      = var.db_port
  redis_port   = var.redis_port
  project_name = var.project_name
  environment  = var.environment
}

module "storage" {
  source = "./modules/storage"

  zappa_s3_bucket = var.zappa_s3_bucket
  project_name    = var.project_name
  environment     = var.environment
}



module "database" {
  source = "./modules/database"

  db_allocated_storage       = var.db_allocated_storage
  db_engine_version          = var.db_engine_version
  db_instance_class          = var.db_instance_class
  db_name                    = var.db_name
  db_password                = var.db_password
  db_username                = var.db_username
  db_storage_type            = var.db_storage_type
  db_backup_retention_period = var.db_backup_retention_period
  db_subnet_ids              = module.networking.private_subnet_ids
  security_group_ids         = [module.security.rds_sg_id]
  proxy_security_group_ids   = [module.security.rds_proxy_sg_id]
  project_name               = var.project_name
  environment                = var.environment
}

module "cache" {
  source = "./modules/cache"

  redis_engine_version  = var.redis_engine_version
  redis_node_type       = var.redis_node_type
  redis_num_cache_nodes = var.redis_num_cache_nodes
  redis_port            = var.redis_port
  redis_auth_token      = var.redis_auth_token
  subnet_ids            = module.networking.private_subnet_ids
  security_group_ids    = [module.security.redis_sg_id]
  project_name          = var.project_name
  environment           = var.environment
}
