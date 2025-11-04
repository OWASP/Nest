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
  db_password          = local.generate_db_password ? random_password.db_password[0].result : var.db_password
  generate_db_password = var.db_password == null || var.db_password == ""
}

resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = var.db_subnet_ids
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-db-subnet-group"
  })
}

resource "random_password" "db_password" {
  count  = local.generate_db_password ? 1 : 0
  length = 32
  # Avoid special characters that might cause issues
  override_special = "!#$%&*()-_=+[]{}<>:?"
  special          = true
}

resource "aws_db_instance" "main" {
  allocated_storage               = var.db_allocated_storage
  backup_retention_period         = var.db_backup_retention_period
  backup_window                   = var.db_backup_window
  copy_tags_to_snapshot           = var.db_copy_tags_to_snapshot
  db_name                         = var.db_name
  db_subnet_group_name            = aws_db_subnet_group.main.name
  enabled_cloudwatch_logs_exports = var.db_enabled_cloudwatch_logs_exports
  engine                          = "postgres"
  engine_version                  = var.db_engine_version
  identifier                      = lower("${var.project_name}-${var.environment}-db")
  instance_class                  = var.db_instance_class
  maintenance_window              = var.db_maintenance_window
  password                        = local.db_password
  publicly_accessible             = false
  skip_final_snapshot             = var.db_skip_final_snapshot
  storage_encrypted               = true
  storage_type                    = var.db_storage_type
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-postgres"
  })
  username               = var.db_user
  vpc_security_group_ids = var.security_group_ids
}

resource "aws_secretsmanager_secret" "db_credentials" {
  description             = "Stores the credentials for the RDS database."
  name                    = "${var.project_name}-${var.environment}-db-credentials"
  recovery_window_in_days = var.secret_recovery_window_in_days
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-db-credentials"
  })
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = var.db_user
    password = local.db_password
  })
}

resource "aws_iam_role" "rds_proxy" {
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "rds.amazonaws.com"
        }
      }
    ]
  })
  name = "${var.project_name}-${var.environment}-rds-proxy-role"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-rds-proxy-role"
  })
}

resource "aws_iam_role_policy" "rds_proxy" {
  name = "${var.project_name}-${var.environment}-rds-proxy-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Effect   = "Allow"
        Resource = aws_secretsmanager_secret.db_credentials.arn
      }
    ]
  })
  role = aws_iam_role.rds_proxy.id
}

resource "aws_db_proxy" "main" {
  auth {
    auth_scheme = "SECRETS"
    description = "Database credentials"
    iam_auth    = "DISABLED"
    secret_arn  = aws_secretsmanager_secret.db_credentials.arn
  }
  debug_logging       = false
  engine_family       = "POSTGRESQL"
  idle_client_timeout = 1800
  name                = "${var.project_name}-${var.environment}-proxy"
  require_tls         = true
  role_arn            = aws_iam_role.rds_proxy.arn
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-rds-proxy"
  })
  vpc_security_group_ids = var.proxy_security_group_ids
  vpc_subnet_ids         = var.db_subnet_ids
}

resource "aws_db_proxy_default_target_group" "main" {
  connection_pool_config {
    connection_borrow_timeout    = 120
    max_connections_percent      = 100
    max_idle_connections_percent = 50
  }
  db_proxy_name = aws_db_proxy.main.name
}

resource "aws_db_proxy_target" "main" {
  db_instance_identifier = aws_db_instance.main.identifier
  db_proxy_name          = aws_db_proxy.main.name
  target_group_name      = aws_db_proxy_default_target_group.main.name
}
