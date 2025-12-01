terraform {
  required_version = "1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.22.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.7.2"
    }
  }
}

resource "aws_security_group" "vpc_endpoints" {
  description = "Security group for VPC endpoints"
  name        = "${var.project_name}-${var.environment}-vpc-endpoints-sg"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-vpc-endpoints-sg"
  })
  vpc_id = var.vpc_id
}

resource "aws_security_group_rule" "vpc_endpoints_ingress_https" {
  cidr_blocks       = [var.vpc_cidr]
  description       = "Allow HTTPS from VPC"
  from_port         = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.vpc_endpoints.id
  to_port           = 443
  type              = "ingress"
}

resource "aws_vpc_endpoint" "cloudwatch_logs" {
  private_dns_enabled = true
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  service_name        = "com.amazonaws.${var.aws_region}.logs"
  subnet_ids          = var.private_subnet_ids
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-cloudwatch-logs-endpoint"
  })
  vpc_endpoint_type = "Interface"
  vpc_id            = var.vpc_id
}

resource "aws_vpc_endpoint" "ecr_api" {
  private_dns_enabled = true
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  service_name        = "com.amazonaws.${var.aws_region}.ecr.api"
  subnet_ids          = var.private_subnet_ids
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-ecr-api-endpoint"
  })
  vpc_endpoint_type = "Interface"
  vpc_id            = var.vpc_id
}

resource "aws_vpc_endpoint" "ecr_dkr" {
  private_dns_enabled = true
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  service_name        = "com.amazonaws.${var.aws_region}.ecr.dkr"
  subnet_ids          = var.private_subnet_ids
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-ecr-dkr-endpoint"
  })
  vpc_endpoint_type = "Interface"
  vpc_id            = var.vpc_id
}

resource "aws_vpc_endpoint" "s3" {
  service_name = "com.amazonaws.${var.aws_region}.s3"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-s3-endpoint"
  })
  vpc_endpoint_type = "Gateway"
  vpc_id            = var.vpc_id
}

resource "aws_vpc_endpoint" "secretsmanager" {
  private_dns_enabled = true
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  service_name        = "com.amazonaws.${var.aws_region}.secretsmanager"
  subnet_ids          = var.private_subnet_ids
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-secretsmanager-endpoint"
  })
  vpc_endpoint_type = "Interface"
  vpc_id            = var.vpc_id
}

resource "aws_vpc_endpoint" "ssm" {
  private_dns_enabled = true
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  service_name        = "com.amazonaws.${var.aws_region}.ssm"
  subnet_ids          = var.private_subnet_ids
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-ssm-endpoint"
  })
  vpc_endpoint_type = "Interface"
  vpc_id            = var.vpc_id
}

resource "aws_vpc_endpoint_route_table_association" "s3_private" {
  route_table_id  = var.private_route_table_id
  vpc_endpoint_id = aws_vpc_endpoint.s3.id
}

resource "aws_vpc_endpoint_route_table_association" "s3_public" {
  route_table_id  = var.public_route_table_id
  vpc_endpoint_id = aws_vpc_endpoint.s3.id
}
