variables {
  common_tags           = { Environment = "test", Project = "nest" }
  environment           = "test"
  log_retention_in_days = 30
  project_name          = "nest"
  redis_engine_version  = "7.0"
  redis_node_type       = "cache.t3.micro"
  redis_num_cache_nodes = 1
  redis_port            = 6379
  security_group_ids    = ["sg-12345678"]
  subnet_ids            = ["subnet-12345678"]
}

run "test_auth_token_generated" {
  command = plan

  assert {
    condition     = length(random_password.redis_auth_token) == 1
    error_message = "Redis auth token must be generated."
  }
}

run "test_auth_token_length" {
  command = plan

  assert {
    condition     = random_password.redis_auth_token[0].length == 32
    error_message = "Redis auth token must be 32 characters."
  }
}

run "test_encryption_enabled_at_rest" {
  command = plan

  assert {
    condition     = aws_elasticache_replication_group.main.at_rest_encryption_enabled
    error_message = "At-rest encryption must be enabled."
  }
}

run "test_encryption_enabled_in_transit" {
  command = plan

  assert {
    condition     = aws_elasticache_replication_group.main.transit_encryption_enabled == true
    error_message = "Transit encryption must be enabled."
  }
}

run "test_engine_is_redis" {
  command = plan

  assert {
    condition     = aws_elasticache_replication_group.main.engine == "redis"
    error_message = "Engine must be Redis."
  }
}

run "test_failover_disabled_for_single_node" {
  command = plan

  assert {
    condition     = aws_elasticache_replication_group.main.automatic_failover_enabled == false
    error_message = "Automatic failover must be disabled for single-node clusters."
  }
}

run "test_failover_enabled_for_multi_node" {
  command = plan

  variables {
    redis_num_cache_nodes = 2
  }

  assert {
    condition     = aws_elasticache_replication_group.main.automatic_failover_enabled == true
    error_message = "Automatic failover must be enabled for multi-node clusters."
  }
}

run "test_log_groups_created" {
  command = plan

  assert {
    condition     = aws_cloudwatch_log_group.engine_log.retention_in_days == var.log_retention_in_days
    error_message = "Engine log group must be created with correct retention."
  }

  assert {
    condition     = aws_cloudwatch_log_group.slow_log.retention_in_days == var.log_retention_in_days
    error_message = "Slow log group must be created with correct retention."
  }
}

run "test_replication_group_id_format" {
  command = plan

  assert {
    condition     = aws_elasticache_replication_group.main.replication_group_id == "${var.project_name}-${var.environment}-cache"
    error_message = "Replication group ID must follow naming convention: {project}-{environment}-cache."
  }
}

run "test_ssm_parameter_is_secure_string" {
  command = plan

  assert {
    condition     = aws_ssm_parameter.django_redis_password.type == "SecureString"
    error_message = "Redis password must be stored as SecureString."
  }
}

run "test_ssm_parameter_path_format" {
  command = plan

  assert {
    condition     = aws_ssm_parameter.django_redis_password.name == "/${var.project_name}/${var.environment}/DJANGO_REDIS_PASSWORD"
    error_message = "SSM parameter must follow path: /{project}/{environment}/DJANGO_REDIS_PASSWORD."
  }
}

run "test_subnet_group_uses_provided_subnets" {
  command = plan

  assert {
    condition     = toset(aws_elasticache_subnet_group.main.subnet_ids) == toset(var.subnet_ids)
    error_message = "Subnet group must use the provided subnet IDs."
  }
}
