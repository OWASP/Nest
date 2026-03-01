terraform {
  required_version = "1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.22.0"
    }
  }
}

resource "aws_network_acl" "private" {
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-private-nacl"
  })
  vpc_id = var.vpc_id
}

resource "aws_network_acl" "public" {
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-public-nacl"
  })
  vpc_id = var.vpc_id
}

resource "aws_network_acl_association" "private" {
  count          = length(var.private_subnet_ids)
  network_acl_id = aws_network_acl.private.id
  subnet_id      = var.private_subnet_ids[count.index]
}

resource "aws_network_acl_association" "public" {
  count          = length(var.public_subnet_ids)
  network_acl_id = aws_network_acl.public.id
  subnet_id      = var.public_subnet_ids[count.index]
}

resource "aws_network_acl_rule" "private_inbound_ephemeral" {
  cidr_block     = "0.0.0.0/0"
  from_port      = 1024
  network_acl_id = aws_network_acl.private.id
  protocol       = "tcp"
  rule_action    = "allow"
  rule_number    = 100
  to_port        = 65535
}

# NACLs are stateless: return traffic for outbound UDP (e.g. DNS, NTP) from private
# instances via NAT arrives from internet hosts, so inbound ephemeral UDP must allow
# 0.0.0.0/0; narrowing to var.vpc_cidr would block those responses.
resource "aws_network_acl_rule" "private_inbound_ephemeral_udp" {
  cidr_block     = "0.0.0.0/0"
  from_port      = 1024
  network_acl_id = aws_network_acl.private.id
  protocol       = "udp"
  rule_action    = "allow"
  rule_number    = 105
  to_port        = 65535
}

resource "aws_network_acl_rule" "private_inbound_https" {
  cidr_block     = var.vpc_cidr
  from_port      = 443
  network_acl_id = aws_network_acl.private.id
  protocol       = "tcp"
  rule_action    = "allow"
  rule_number    = 110
  to_port        = 443
}

resource "aws_network_acl_rule" "private_inbound_postgres" {
  cidr_block     = var.vpc_cidr
  from_port      = 5432
  network_acl_id = aws_network_acl.private.id
  protocol       = "tcp"
  rule_action    = "allow"
  rule_number    = 120
  to_port        = 5432
}

resource "aws_network_acl_rule" "private_inbound_redis" {
  cidr_block     = var.vpc_cidr
  from_port      = 6379
  network_acl_id = aws_network_acl.private.id
  protocol       = "tcp"
  rule_action    = "allow"
  rule_number    = 130
  to_port        = 6379
}

resource "aws_network_acl_rule" "private_outbound_all" {
  cidr_block     = "0.0.0.0/0"
  egress         = true
  from_port      = 0
  network_acl_id = aws_network_acl.private.id
  protocol       = "-1"
  rule_action    = "allow"
  rule_number    = 100
  to_port        = 0
}

resource "aws_network_acl_rule" "public_inbound_ephemeral" {
  cidr_block     = "0.0.0.0/0"
  from_port      = 1024
  network_acl_id = aws_network_acl.public.id
  protocol       = "tcp"
  rule_action    = "allow"
  rule_number    = 100
  to_port        = 65535
}

resource "aws_network_acl_rule" "public_inbound_ephemeral_udp" {
  cidr_block     = "0.0.0.0/0"
  from_port      = 1024
  network_acl_id = aws_network_acl.public.id
  protocol       = "udp"
  rule_action    = "allow"
  rule_number    = 105
  to_port        = 65535
}

resource "aws_network_acl_rule" "public_inbound_http" {
  cidr_block     = "0.0.0.0/0"
  from_port      = 80
  network_acl_id = aws_network_acl.public.id
  protocol       = "tcp"
  rule_action    = "allow"
  rule_number    = 110
  to_port        = 80
}

resource "aws_network_acl_rule" "public_inbound_https" {
  cidr_block     = "0.0.0.0/0"
  from_port      = 443
  network_acl_id = aws_network_acl.public.id
  protocol       = "tcp"
  rule_action    = "allow"
  rule_number    = 120
  to_port        = 443
}

resource "aws_network_acl_rule" "public_outbound_all" {
  cidr_block     = "0.0.0.0/0"
  egress         = true
  from_port      = 0
  network_acl_id = aws_network_acl.public.id
  protocol       = "-1"
  rule_action    = "allow"
  rule_number    = 100
  to_port        = 0
}
