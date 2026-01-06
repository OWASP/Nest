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

  common_tags                    = local.common_tags
  create_rds_proxy               = var.create_rds_proxy
  db_allocated_storage           = var.db_allocated_storage
  db_backup_retention_period     = var.db_backup_retention_period
  db_deletion_protection         = var.db_deletion_protection
  db_engine_version              = var.db_engine_version
  db_instance_class              = var.db_instance_class
  db_name                        = var.db_name
  db_password                    = var.db_password
  db_skip_final_snapshot         = var.db_skip_final_snapshot
  db_storage_type                = var.db_storage_type
  db_subnet_ids                  = module.networking.private_subnet_ids
  db_user                        = var.db_user
  environment                    = var.environment
  project_name                   = var.project_name
  proxy_security_group_ids       = [module.security.rds_proxy_sg_id]
  secret_recovery_window_in_days = var.secret_recovery_window_in_days
  security_group_ids             = [module.security.rds_sg_id]
}

module "ecs" {
  source = "../modules/ecs"

  assign_public_ip              = var.ecs_use_public_subnets
  aws_region                    = var.aws_region
  common_tags                   = local.common_tags
  container_parameters_arns     = module.parameters.django_ssm_parameter_arns
  ecs_sg_id                     = module.security.ecs_sg_id
  environment                   = var.environment
  fixtures_bucket_name          = module.storage.fixtures_s3_bucket_name
  fixtures_read_only_policy_arn = module.storage.fixtures_read_only_policy_arn
  project_name                  = var.project_name
  subnet_ids                    = var.ecs_use_public_subnets ? module.networking.public_subnet_ids : module.networking.private_subnet_ids
  use_fargate_spot              = var.use_fargate_spot
}

module "frontend" {
  source = "../modules/frontend"

  alb_sg_id                = module.security.alb_sg_id
  aws_region               = var.aws_region
  common_tags              = local.common_tags
  desired_count            = var.frontend_desired_count
  domain_name              = var.frontend_domain_name
  enable_auto_scaling      = var.frontend_enable_auto_scaling
  enable_https             = var.frontend_domain_name != null
  environment              = var.environment
  frontend_parameters_arns = module.parameters.frontend_ssm_parameter_arns
  frontend_sg_id           = module.security.frontend_sg_id
  max_count                = var.frontend_max_count
  min_count                = var.frontend_min_count
  private_subnet_ids       = module.networking.private_subnet_ids
  project_name             = var.project_name
  public_subnet_ids        = module.networking.public_subnet_ids
  use_fargate_spot         = var.frontend_use_fargate_spot
  vpc_id                   = module.networking.vpc_id
}

module "networking" {
  source = "../modules/networking"

  aws_region                          = var.aws_region
  availability_zones                  = var.availability_zones
  common_tags                         = local.common_tags
  create_nat_gateway                  = var.create_nat_gateway
  create_vpc_cloudwatch_logs_endpoint = var.create_vpc_cloudwatch_logs_endpoint
  create_vpc_ecr_api_endpoint         = var.create_vpc_ecr_api_endpoint
  create_vpc_ecr_dkr_endpoint         = var.create_vpc_ecr_dkr_endpoint
  create_vpc_s3_endpoint              = var.create_vpc_s3_endpoint
  create_vpc_secretsmanager_endpoint  = var.create_vpc_secretsmanager_endpoint
  create_vpc_ssm_endpoint             = var.create_vpc_ssm_endpoint
  environment                         = var.environment
  private_subnet_cidrs                = var.private_subnet_cidrs
  project_name                        = var.project_name
  public_subnet_cidrs                 = var.public_subnet_cidrs
  vpc_cidr                            = var.vpc_cidr
}

module "parameters" {
  source = "../modules/parameters"

  allowed_origins    = var.frontend_domain_name != null ? "https://${var.frontend_domain_name}" : "http://${module.frontend.alb_dns_name}"
  common_tags        = local.common_tags
  db_host            = module.database.db_proxy_endpoint
  db_name            = var.db_name
  db_password_arn    = module.database.db_password_arn
  db_port            = var.db_port
  db_user            = var.db_user
  environment        = var.environment
  nextauth_url       = var.frontend_domain_name != null ? "https://${var.frontend_domain_name}" : "http://${module.frontend.alb_dns_name}"
  project_name       = var.project_name
  redis_host         = module.cache.redis_primary_endpoint
  redis_password_arn = module.cache.redis_password_arn
}

module "security" {
  source = "../modules/security"

  common_tags               = local.common_tags
  create_rds_proxy          = var.create_rds_proxy
  create_vpc_endpoint_rules = var.create_vpc_ssm_endpoint || var.create_vpc_cloudwatch_logs_endpoint || var.create_vpc_ecr_api_endpoint || var.create_vpc_ecr_dkr_endpoint || var.create_vpc_secretsmanager_endpoint
  db_port                   = var.db_port
  environment               = var.environment
  project_name              = var.project_name
  redis_port                = var.redis_port
  vpc_endpoint_sg_id        = module.networking.vpc_endpoint_security_group_id
  vpc_id                    = module.networking.vpc_id
}

module "storage" {
  source = "../modules/storage"

  common_tags          = local.common_tags
  environment          = var.environment
  fixtures_bucket_name = var.fixtures_bucket_name
  project_name         = var.project_name
  zappa_bucket_name    = var.zappa_bucket_name
}
