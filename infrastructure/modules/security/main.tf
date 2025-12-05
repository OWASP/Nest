terraform {
  required_version = "1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.22.0"
    }
  }
}

resource "aws_security_group" "ecs" {
  description = "Security group for ECS tasks"
  name        = "${var.project_name}-${var.environment}-ecs-sg"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-ecs-sg"
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

resource "aws_security_group_rule" "ecs_to_vpc_endpoints" {
  description              = "Allow HTTPS to VPC endpoints"
  from_port                = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.ecs.id
  source_security_group_id = var.vpc_endpoint_sg_id
  to_port                  = 443
  type                     = "egress"
}

resource "aws_security_group_rule" "lambda_to_vpc_endpoints" {
  description              = "Allow HTTPS to VPC endpoints"
  from_port                = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.lambda.id
  source_security_group_id = var.vpc_endpoint_sg_id
  to_port                  = 443
  type                     = "egress"
}

resource "aws_security_group_rule" "rds_from_ecs" {
  count                    = var.create_rds_proxy ? 0 : 1
  description              = "PostgreSQL from ECS"
  from_port                = var.db_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.rds.id
  source_security_group_id = aws_security_group.ecs.id
  to_port                  = var.db_port
  type                     = "ingress"
}

resource "aws_security_group_rule" "rds_from_lambda" {
  count                    = var.create_rds_proxy ? 0 : 1
  description              = "PostgreSQL from Lambda"
  from_port                = var.db_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.rds.id
  source_security_group_id = aws_security_group.lambda.id
  to_port                  = var.db_port
  type                     = "ingress"
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

resource "aws_security_group_rule" "rds_proxy_from_ecs" {
  count                    = var.create_rds_proxy ? 1 : 0
  type                     = "ingress"
  description              = "PostgreSQL from ECS"
  from_port                = var.db_port
  to_port                  = var.db_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.rds_proxy[0].id
  source_security_group_id = aws_security_group.ecs.id
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

resource "aws_security_group_rule" "redis_from_ecs" {
  description              = "Redis from ECS"
  from_port                = var.redis_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.redis.id
  source_security_group_id = aws_security_group.ecs.id
  to_port                  = var.redis_port
  type                     = "ingress"
}
