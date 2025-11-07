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

resource "aws_security_group" "lambda" {
  description = "Security group for Lambda functions (Zappa)"
  name        = "${var.project_name}-${var.environment}-lambda-sg"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-lambda-sg"
  })
  vpc_id = var.vpc_id

  egress {
    cidr_blocks = var.default_egress_cidr_blocks
    description = "Allow all outbound traffic"
    from_port   = 0
    protocol    = "-1"
    to_port     = 0
  }
}

resource "aws_security_group" "rds" {
  description = "Security group for RDS PostgreSQL"
  name        = "${var.project_name}-${var.environment}-rds-sg"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-rds-sg"
  })
  vpc_id = var.vpc_id

  egress {
    cidr_blocks = var.default_egress_cidr_blocks
    description = "Allow all outbound traffic"
    from_port   = 0
    protocol    = "-1"
    to_port     = 0
  }
}

resource "aws_security_group" "rds_proxy" {
  count       = var.create_rds_proxy ? 1 : 0
  description = "Security group for RDS Proxy"
  name        = "${var.project_name}-${var.environment}-rds-proxy-sg"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-rds-proxy-sg"
  })
  vpc_id = var.vpc_id

  egress {
    cidr_blocks = var.default_egress_cidr_blocks
    description = "Allow all outbound traffic"
    from_port   = 0
    protocol    = "-1"
    to_port     = 0
  }
}

resource "aws_security_group" "redis" {
  description = "Security group for ElastiCache Redis"
  name        = "${var.project_name}-${var.environment}-redis-sg"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-redis-sg"
  })
  vpc_id = var.vpc_id

  egress {
    cidr_blocks = var.default_egress_cidr_blocks
    description = "Allow all outbound traffic"
    from_port   = 0
    protocol    = "-1"
    to_port     = 0
  }

  ingress {
    description     = "Redis from Lambda"
    from_port       = var.redis_port
    protocol        = "tcp"
    security_groups = [aws_security_group.lambda.id]
    to_port         = var.redis_port
  }
}

resource "aws_security_group_rule" "rds_from_proxy" {
  count                    = var.create_rds_proxy ? 1 : 0
  type                     = "ingress"
  description              = "PostgreSQL from RDS Proxy"
  from_port                = var.db_port
  to_port                  = var.db_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.rds.id
  source_security_group_id = aws_security_group.rds_proxy[0].id
}

resource "aws_security_group_rule" "rds_proxy_from_lambda" {
  count                    = var.create_rds_proxy ? 1 : 0
  type                     = "ingress"
  description              = "PostgreSQL from Lambda"
  from_port                = var.db_port
  to_port                  = var.db_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.rds_proxy[0].id
  source_security_group_id = aws_security_group.lambda.id
}
