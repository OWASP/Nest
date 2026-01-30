variables {
  common_tags          = { Environment = "test", Project = "nest" }
  create_rds_proxy     = false
  db_allocated_storage = 20
  db_engine_version    = "16.4"
  db_instance_class    = "db.t3.micro"
  db_name              = "nest_db"
  db_subnet_ids        = ["subnet-12345678"]
  db_user              = "nest_user"
  environment          = "test"
  kms_key_arn          = "arn:aws:kms:us-east-2:123456789012:key/12345678-1234-1234-1234-123456789012"
  project_name         = "nest"
  security_group_ids   = ["sg-12345678"]
}

run "test_database_not_publicly_accessible" {
  command = plan

  assert {
    condition     = aws_db_instance.main.publicly_accessible == false
    error_message = "Database must not be publicly accessible."
  }
}

run "test_db_identifier_format" {
  command = plan

  assert {
    condition     = aws_db_instance.main.identifier == lower("${var.project_name}-${var.environment}-db")
    error_message = "Database identifier must follow naming convention: {project}-{environment}-db."
  }
}

run "test_deletion_protection_enabled" {
  command = plan

  assert {
    condition     = aws_db_instance.main.deletion_protection
    error_message = "Deletion protection must be enabled by default."
  }
}

run "test_engine_is_postgres" {
  command = plan

  assert {
    condition     = aws_db_instance.main.engine == "postgres"
    error_message = "Database engine must be postgres."
  }
}

run "test_password_generated_when_not_provided" {
  command = plan

  assert {
    condition     = length(random_password.db_password) == 1
    error_message = "Database password must be generated when not provided."
  }
}

run "test_password_not_generated_when_provided" {
  command = plan

  variables {
    db_password = "test-password-123"
  }

  assert {
    condition     = length(random_password.db_password) == 0
    error_message = "Database password must not be generated when provided."
  }
}

run "test_proxy_created_when_enabled" {
  command = plan

  variables {
    create_rds_proxy         = true
    proxy_security_group_ids = ["sg-proxy12345"]
  }

  assert {
    condition     = length(aws_db_proxy.main) == 1
    error_message = "RDS proxy must be created when create_rds_proxy is true."
  }
}

run "test_proxy_engine_family" {
  command = plan

  variables {
    create_rds_proxy         = true
    proxy_security_group_ids = ["sg-proxy12345"]
  }

  assert {
    condition     = aws_db_proxy.main[0].engine_family == "POSTGRESQL"
    error_message = "RDS proxy engine family must be POSTGRESQL."
  }
}

run "test_proxy_not_created_when_disabled" {
  command = plan

  assert {
    condition     = length(aws_db_proxy.main) == 0
    error_message = "RDS proxy must not be created when create_rds_proxy is false."
  }
}

run "test_proxy_requires_tls" {
  command = plan

  variables {
    create_rds_proxy         = true
    proxy_security_group_ids = ["sg-proxy12345"]
  }

  assert {
    condition     = aws_db_proxy.main[0].require_tls
    error_message = "RDS proxy must require TLS."
  }
}

run "test_ssm_parameter_is_secure_string" {
  command = plan

  assert {
    condition     = aws_ssm_parameter.django_db_password.type == "SecureString"
    error_message = "Database password must be stored as SecureString."
  }
}

run "test_ssm_parameter_path_format" {
  command = plan

  assert {
    condition     = aws_ssm_parameter.django_db_password.name == "/${var.project_name}/${var.environment}/DJANGO_DB_PASSWORD"
    error_message = "SSM parameter must follow path: /{project}/{environment}/DJANGO_DB_PASSWORD."
  }
}

run "test_storage_encrypted" {
  command = plan

  assert {
    condition     = aws_db_instance.main.storage_encrypted
    error_message = "Database storage must be encrypted."
  }
}

run "test_subnet_group_uses_provided_subnets" {
  command = plan

  assert {
    condition     = toset(aws_db_subnet_group.main.subnet_ids) == toset(var.db_subnet_ids)
    error_message = "Subnet group must use the provided subnet IDs."
  }
}
