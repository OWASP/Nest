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
  fixtures_bucket_name = coalesce(var.fixtures_bucket_name, "${var.project_name}-${var.environment}-fixtures")
}

module "alb" {
  source = "../modules/alb"

  alb_sg_id                  = module.security.alb_sg_id
  common_tags                = local.common_tags
  domain_name                = var.domain_name
  environment                = var.environment
  frontend_health_check_path = "/"
  frontend_port              = 3000
  project_name               = var.project_name
  public_subnet_ids          = module.networking.public_subnet_ids
  vpc_id                     = module.networking.vpc_id
}

module "backend" {
  source = "../modules/service"

  aws_region          = var.aws_region
  command             = ["./entrypoint.sh"]
  common_tags         = local.common_tags
  container_cpu       = 1024
  container_memory    = 2048
  container_port      = 8000
  desired_count       = var.backend_desired_count
  enable_auto_scaling = var.backend_enable_auto_scaling
  environment         = var.environment
  kms_key_arn         = module.kms.key_arn
  max_count           = var.backend_max_count
  min_count           = var.backend_min_count
  parameters_arns     = module.parameters.django_ssm_parameter_arns
  private_subnet_ids  = module.networking.private_subnet_ids
  project_name        = var.project_name
  security_group_id   = module.security.backend_sg_id
  service_name        = "backend"
  target_group_arn    = module.alb.backend_target_group_arn
  use_fargate_spot    = var.backend_use_fargate_spot
}

module "cache" {
  source = "../modules/cache"

  common_tags           = local.common_tags
  environment           = var.environment
  kms_key_arn           = module.kms.key_arn
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
  kms_key_arn                    = module.kms.key_arn
  project_name                   = var.project_name
  proxy_security_group_ids       = [module.security.rds_proxy_sg_id]
  secret_recovery_window_in_days = var.secret_recovery_window_in_days
  security_group_ids             = [module.security.rds_sg_id]
}

module "frontend" {
  source = "../modules/service"

  aws_region          = var.aws_region
  common_tags         = local.common_tags
  container_port      = 3000
  desired_count       = var.frontend_desired_count
  enable_auto_scaling = var.frontend_enable_auto_scaling
  environment         = var.environment
  kms_key_arn         = module.kms.key_arn
  max_count           = var.frontend_max_count
  min_count           = var.frontend_min_count
  parameters_arns     = module.parameters.frontend_ssm_parameter_arns
  private_subnet_ids  = module.networking.private_subnet_ids
  project_name        = var.project_name
  security_group_id   = module.security.frontend_sg_id
  service_name        = "frontend"
  target_group_arn    = module.alb.frontend_target_group_arn
  use_fargate_spot    = var.frontend_use_fargate_spot
}

module "kms" {
  source = "../modules/kms"

  common_tags  = local.common_tags
  environment  = var.environment
  project_name = var.project_name
}

module "networking" {
  source = "../modules/networking"

  aws_region                          = var.aws_region
  availability_zones                  = var.availability_zones
  common_tags                         = local.common_tags
  create_vpc_cloudwatch_logs_endpoint = var.create_vpc_cloudwatch_logs_endpoint
  create_vpc_ecr_api_endpoint         = var.create_vpc_ecr_api_endpoint
  create_vpc_ecr_dkr_endpoint         = var.create_vpc_ecr_dkr_endpoint
  create_vpc_s3_endpoint              = var.create_vpc_s3_endpoint
  create_vpc_secretsmanager_endpoint  = var.create_vpc_secretsmanager_endpoint
  create_vpc_ssm_endpoint             = var.create_vpc_ssm_endpoint
  environment                         = var.environment
  kms_key_arn                         = module.kms.key_arn
  private_subnet_cidrs                = var.private_subnet_cidrs
  project_name                        = var.project_name
  public_subnet_cidrs                 = var.public_subnet_cidrs
  vpc_cidr                            = var.vpc_cidr
}

module "parameters" {
  source = "../modules/parameters"

  allowed_hosts      = var.domain_name
  allowed_origins    = "https://${var.domain_name}"
  common_tags        = local.common_tags
  db_host            = module.database.db_proxy_endpoint
  db_name            = var.db_name
  db_password_arn    = module.database.db_password_arn
  db_port            = var.db_port
  db_user            = var.db_user
  environment        = var.environment
  nextauth_url       = "https://${var.domain_name}"
  project_name       = var.project_name
  redis_host         = module.cache.redis_primary_endpoint
  redis_password_arn = module.cache.redis_password_arn
  server_csrf_url    = "https://${var.domain_name}/csrf/"
  server_graphql_url = "https://${var.domain_name}/graphql/"
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
  fixtures_bucket_name = local.fixtures_bucket_name
  project_name         = var.project_name
}

module "tasks" {
  source = "../modules/tasks"

  assign_public_ip              = var.ecs_assign_public_ip
  aws_region                    = var.aws_region
  common_tags                   = local.common_tags
  container_parameters_arns     = module.parameters.django_ssm_parameter_arns
  ecr_repository_arn            = module.backend.ecr_repository_arn
  ecr_repository_url            = module.backend.ecr_repository_url
  ecs_sg_id                     = module.security.tasks_sg_id
  environment                   = var.environment
  fixtures_bucket_name          = module.storage.fixtures_s3_bucket_name
  fixtures_read_only_policy_arn = module.storage.fixtures_read_only_policy_arn
  kms_key_arn                   = module.kms.key_arn
  project_name                  = var.project_name
  subnet_ids                    = var.ecs_assign_public_ip ? module.networking.public_subnet_ids : module.networking.private_subnet_ids
  use_fargate_spot              = var.tasks_use_fargate_spot
}
