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

# ElastiCache Subnet Group
resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-cache-subnet-group"
  subnet_ids = var.subnet_ids

  tags = {
    Name = "${var.project_name}-${var.environment}-cache-subnet-group"
  }
}

# Random auth token for Redis (if not provided)
resource "random_password" "redis_auth_token" {
  count = var.redis_auth_token == null || var.redis_auth_token == "" ? 1 : 0

  length  = 32
  special = true
  # Redis auth token has specific requirements
  override_special = "!&#$^<>-"
}

# ElastiCache Redis Replication Group
resource "aws_elasticache_replication_group" "main" {
  replication_group_id = "${var.project_name}-${var.environment}-cache"
  description          = "${var.project_name} ${var.environment} Redis cache"

  engine               = "redis"
  engine_version       = var.redis_engine_version
  node_type            = var.redis_node_type
  port                 = var.redis_port
  parameter_group_name = "default.redis${split(".", var.redis_engine_version)[0]}"

  # Cluster configuration
  num_cache_clusters = var.redis_num_cache_nodes

  # Network configuration
  subnet_group_name  = aws_elasticache_subnet_group.main.name
  security_group_ids = var.security_group_ids

  # Security
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                 = var.redis_auth_token != null && var.redis_auth_token != "" ? var.redis_auth_token : random_password.redis_auth_token[0].result

  # Maintenance and backups
  snapshot_retention_limit = 5
  snapshot_window          = "03:00-05:00"
  maintenance_window       = "mon:05:00-mon:07:00"

  # Automatic failover (requires at least 2 nodes)
  automatic_failover_enabled = var.redis_num_cache_nodes > 1

  # Enable automatic minor version upgrades
  auto_minor_version_upgrade = true

  tags = {
    Name = "${var.project_name}-${var.environment}-redis"
  }
}
