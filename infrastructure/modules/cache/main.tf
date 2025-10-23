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
  generate_redis_auth_token = var.redis_auth_token == null || var.redis_auth_token == ""
  parameter_group_name      = "default.redis${local.redis_major_version}"
  redis_auth_token          = local.generate_redis_auth_token ? random_password.redis_auth_token[0].result : var.redis_auth_token
  redis_major_version       = split(".", var.redis_engine_version)[0]
}

resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-cache-subnet-group"
  subnet_ids = var.subnet_ids
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-cache-subnet-group"
  })
}

resource "random_password" "redis_auth_token" {
  count  = local.generate_redis_auth_token ? 1 : 0
  length = 32
  # Redis auth token has specific requirements for special characters.
  override_special = "!&#$^<>-"
  special          = true
}

resource "aws_elasticache_replication_group" "main" {
  at_rest_encryption_enabled = true
  auth_token                 = local.redis_auth_token
  auto_minor_version_upgrade = var.auto_minor_version_upgrade
  automatic_failover_enabled = var.redis_num_cache_nodes > 1
  description                = "${var.project_name} ${var.environment} Redis cache"
  engine                     = "redis"
  engine_version             = var.redis_engine_version
  maintenance_window         = var.maintenance_window
  node_type                  = var.redis_node_type
  num_cache_clusters         = var.redis_num_cache_nodes
  parameter_group_name       = local.parameter_group_name
  port                       = var.redis_port
  replication_group_id       = "${var.project_name}-${var.environment}-cache"
  security_group_ids         = var.security_group_ids
  snapshot_retention_limit   = var.snapshot_retention_limit
  snapshot_window            = var.snapshot_window
  subnet_group_name          = aws_elasticache_subnet_group.main.name
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-redis"
  })
  transit_encryption_enabled = true
}
