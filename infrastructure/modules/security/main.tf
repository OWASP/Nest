terraform {
  required_version = "1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.22.0"
    }
  }
}

check "vpc_endpoint_rules_require_sg" {
  assert {
    condition     = var.create_vpc_endpoint_rules ? var.vpc_endpoint_sg_id != null : true
    error_message = "vpc_endpoint_sg_id must be provided when create_vpc_endpoint_rules is true."
  }
}

resource "aws_security_group" "alb" {
  description = "Security group for Application Load Balancer"
  name        = "${var.project_name}-${var.environment}-alb-sg"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-alb-sg"
  })
  vpc_id = var.vpc_id
}

resource "aws_security_group" "ecs" {
  description = "Security group for ECS tasks"
  name        = "${var.project_name}-${var.environment}-ecs-sg"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-ecs-sg"
  })
  vpc_id = var.vpc_id
}

resource "aws_security_group" "frontend" {
  description = "Security group for frontend ECS tasks"
  name        = "${var.project_name}-${var.environment}-frontend-sg"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-frontend-sg"
  })
  vpc_id = var.vpc_id
}

resource "aws_security_group" "lambda" {
  description = "Security group for Lambda functions (Zappa)"
  name        = "${var.project_name}-${var.environment}-lambda-sg"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-lambda-sg"
  })
  vpc_id = var.vpc_id
}

resource "aws_security_group" "rds" {
  description = "Security group for RDS PostgreSQL"
  name        = "${var.project_name}-${var.environment}-rds-sg"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-rds-sg"
  })
  vpc_id = var.vpc_id
}

resource "aws_security_group" "rds_proxy" {
  count       = var.create_rds_proxy ? 1 : 0
  description = "Security group for RDS Proxy"
  name        = "${var.project_name}-${var.environment}-rds-proxy-sg"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-rds-proxy-sg"
  })
  vpc_id = var.vpc_id
}

resource "aws_security_group" "redis" {
  description = "Security group for ElastiCache Redis"
  name        = "${var.project_name}-${var.environment}-redis-sg"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-redis-sg"
  })
  vpc_id = var.vpc_id
}

resource "aws_security_group_rule" "alb_http" {
  cidr_blocks       = ["0.0.0.0/0"]
  description       = "Allow HTTP from internet"
  from_port         = 80
  protocol          = "tcp"
  security_group_id = aws_security_group.alb.id
  to_port           = 80
  type              = "ingress"
}

resource "aws_security_group_rule" "alb_https" {
  cidr_blocks       = ["0.0.0.0/0"]
  description       = "Allow HTTPS from internet"
  from_port         = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.alb.id
  to_port           = 443
  type              = "ingress"
}

resource "aws_security_group_rule" "alb_to_frontend" {
  description              = "Allow traffic to frontend ECS tasks"
  from_port                = 3000
  protocol                 = "tcp"
  security_group_id        = aws_security_group.alb.id
  source_security_group_id = aws_security_group.frontend.id
  to_port                  = 3000
  type                     = "egress"
}

resource "aws_security_group_rule" "ecs_egress_all" {
  cidr_blocks       = var.default_egress_cidr_blocks
  description       = "Allow all outbound traffic"
  from_port         = 0
  protocol          = "-1"
  security_group_id = aws_security_group.ecs.id
  to_port           = 0
  type              = "egress"
}

resource "aws_security_group_rule" "ecs_to_vpc_endpoints" {
  count                    = var.create_vpc_endpoint_rules ? 1 : 0
  description              = "Allow HTTPS to VPC endpoints"
  from_port                = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.ecs.id
  source_security_group_id = var.vpc_endpoint_sg_id
  to_port                  = 443
  type                     = "egress"
}

resource "aws_security_group_rule" "frontend_from_alb" {
  description              = "Allow traffic from ALB"
  from_port                = 3000
  protocol                 = "tcp"
  security_group_id        = aws_security_group.frontend.id
  source_security_group_id = aws_security_group.alb.id
  to_port                  = 3000
  type                     = "ingress"
}

resource "aws_security_group_rule" "frontend_https" {
  cidr_blocks       = ["0.0.0.0/0"]
  description       = "Allow HTTPS for external API calls"
  from_port         = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.frontend.id
  to_port           = 443
  type              = "egress"
}

resource "aws_security_group_rule" "frontend_to_vpc_endpoints" {
  count                    = var.create_vpc_endpoint_rules ? 1 : 0
  description              = "Allow HTTPS to VPC endpoints"
  from_port                = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.frontend.id
  source_security_group_id = var.vpc_endpoint_sg_id
  to_port                  = 443
  type                     = "egress"
}

resource "aws_security_group_rule" "lambda_egress_all" {
  cidr_blocks       = var.default_egress_cidr_blocks
  description       = "Allow all outbound traffic"
  from_port         = 0
  protocol          = "-1"
  security_group_id = aws_security_group.lambda.id
  to_port           = 0
  type              = "egress"
}

resource "aws_security_group_rule" "lambda_to_vpc_endpoints" {
  count                    = var.create_vpc_endpoint_rules ? 1 : 0
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
  description              = "PostgreSQL from RDS Proxy"
  from_port                = var.db_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.rds.id
  source_security_group_id = aws_security_group.rds_proxy[0].id
  to_port                  = var.db_port
  type                     = "ingress"
}

resource "aws_security_group_rule" "rds_proxy_to_rds" {
  count                    = var.create_rds_proxy ? 1 : 0
  description              = "Allow RDS Proxy to reach RDS database"
  from_port                = var.db_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.rds_proxy[0].id
  source_security_group_id = aws_security_group.rds.id
  to_port                  = var.db_port
  type                     = "egress"
}

resource "aws_security_group_rule" "rds_proxy_from_ecs" {
  count                    = var.create_rds_proxy ? 1 : 0
  description              = "PostgreSQL from ECS"
  from_port                = var.db_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.rds_proxy[0].id
  source_security_group_id = aws_security_group.ecs.id
  to_port                  = var.db_port
  type                     = "ingress"
}

resource "aws_security_group_rule" "rds_proxy_from_lambda" {
  count                    = var.create_rds_proxy ? 1 : 0
  description              = "PostgreSQL from Lambda"
  from_port                = var.db_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.rds_proxy[0].id
  source_security_group_id = aws_security_group.lambda.id
  to_port                  = var.db_port
  type                     = "ingress"
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

resource "aws_security_group_rule" "redis_from_lambda" {
  description              = "Redis from Lambda"
  from_port                = var.redis_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.redis.id
  source_security_group_id = aws_security_group.lambda.id
  to_port                  = var.redis_port
  type                     = "ingress"
}
