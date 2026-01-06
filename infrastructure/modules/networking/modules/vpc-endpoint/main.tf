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
  # Check if any interface endpoints are enabled (need security group)
  any_interface_endpoint = var.create_cloudwatch_logs || var.create_ecr_api || var.create_ecr_dkr || var.create_secretsmanager || var.create_ssm
}

resource "aws_security_group" "vpc_endpoints" {
  count       = local.any_interface_endpoint ? 1 : 0
  description = "Security group for VPC endpoints"
  name        = "${var.project_name}-${var.environment}-vpc-endpoints-sg"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-vpc-endpoints-sg"
  })
  vpc_id = var.vpc_id
}

resource "aws_security_group_rule" "vpc_endpoints_ingress_https" {
  count             = local.any_interface_endpoint ? 1 : 0
  cidr_blocks       = [var.vpc_cidr]
  description       = "Allow HTTPS from VPC"
  from_port         = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.vpc_endpoints[0].id
  to_port           = 443
  type              = "ingress"
}

resource "aws_vpc_endpoint" "cloudwatch_logs" {
  count               = var.create_cloudwatch_logs ? 1 : 0
  private_dns_enabled = true
  security_group_ids  = [aws_security_group.vpc_endpoints[0].id]
  service_name        = "com.amazonaws.${var.aws_region}.logs"
  subnet_ids          = var.private_subnet_ids
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-cloudwatch-logs-endpoint"
  })
  vpc_endpoint_type = "Interface"
  vpc_id            = var.vpc_id
}

resource "aws_vpc_endpoint" "ecr_api" {
  count               = var.create_ecr_api ? 1 : 0
  private_dns_enabled = true
  security_group_ids  = [aws_security_group.vpc_endpoints[0].id]
  service_name        = "com.amazonaws.${var.aws_region}.ecr.api"
  subnet_ids          = var.private_subnet_ids
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-ecr-api-endpoint"
  })
  vpc_endpoint_type = "Interface"
  vpc_id            = var.vpc_id
}

resource "aws_vpc_endpoint" "ecr_dkr" {
  count               = var.create_ecr_dkr ? 1 : 0
  private_dns_enabled = true
  security_group_ids  = [aws_security_group.vpc_endpoints[0].id]
  service_name        = "com.amazonaws.${var.aws_region}.ecr.dkr"
  subnet_ids          = var.private_subnet_ids
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-ecr-dkr-endpoint"
  })
  vpc_endpoint_type = "Interface"
  vpc_id            = var.vpc_id
}

resource "aws_vpc_endpoint" "s3" {
  count        = var.create_s3 ? 1 : 0
  service_name = "com.amazonaws.${var.aws_region}.s3"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-s3-endpoint"
  })
  vpc_endpoint_type = "Gateway"
  vpc_id            = var.vpc_id
}

resource "aws_vpc_endpoint" "secretsmanager" {
  count               = var.create_secretsmanager ? 1 : 0
  private_dns_enabled = true
  security_group_ids  = [aws_security_group.vpc_endpoints[0].id]
  service_name        = "com.amazonaws.${var.aws_region}.secretsmanager"
  subnet_ids          = var.private_subnet_ids
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-secretsmanager-endpoint"
  })
  vpc_endpoint_type = "Interface"
  vpc_id            = var.vpc_id
}

resource "aws_vpc_endpoint" "ssm" {
  count               = var.create_ssm ? 1 : 0
  private_dns_enabled = true
  security_group_ids  = [aws_security_group.vpc_endpoints[0].id]
  service_name        = "com.amazonaws.${var.aws_region}.ssm"
  subnet_ids          = var.private_subnet_ids
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-ssm-endpoint"
  })
  vpc_endpoint_type = "Interface"
  vpc_id            = var.vpc_id
}

resource "aws_vpc_endpoint_route_table_association" "s3_private" {
  count           = var.create_s3 ? 1 : 0
  route_table_id  = var.private_route_table_id
  vpc_endpoint_id = aws_vpc_endpoint.s3[0].id
}

resource "aws_vpc_endpoint_route_table_association" "s3_public" {
  count           = var.create_s3 ? 1 : 0
  route_table_id  = var.public_route_table_id
  vpc_endpoint_id = aws_vpc_endpoint.s3[0].id
}
