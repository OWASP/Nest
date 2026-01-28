terraform {
  required_version = "1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.22.0"
    }
  }
}

data "aws_iam_policy_document" "flow_logs_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["vpc-flow-logs.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "flow_logs_policy" {
  statement {
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogStreams",
    ]
    resources = ["${aws_cloudwatch_log_group.flow_logs.arn}:*"]
  }
}

module "nacl" {
  source = "./modules/nacl"

  common_tags        = var.common_tags
  environment        = var.environment
  private_subnet_ids = aws_subnet.private[*].id
  project_name       = var.project_name
  public_subnet_ids  = aws_subnet.public[*].id
  vpc_cidr           = var.vpc_cidr
  vpc_id             = aws_vpc.main.id
}

module "vpc_endpoint" {
  count  = (var.create_vpc_cloudwatch_logs_endpoint || var.create_vpc_ecr_api_endpoint || var.create_vpc_ecr_dkr_endpoint || var.create_vpc_s3_endpoint || var.create_vpc_secretsmanager_endpoint || var.create_vpc_ssm_endpoint) ? 1 : 0
  source = "./modules/vpc-endpoint"

  aws_region             = var.aws_region
  common_tags            = var.common_tags
  create_cloudwatch_logs = var.create_vpc_cloudwatch_logs_endpoint
  create_ecr_api         = var.create_vpc_ecr_api_endpoint
  create_ecr_dkr         = var.create_vpc_ecr_dkr_endpoint
  create_s3              = var.create_vpc_s3_endpoint
  create_secretsmanager  = var.create_vpc_secretsmanager_endpoint
  create_ssm             = var.create_vpc_ssm_endpoint
  environment            = var.environment
  private_route_table_id = aws_route_table.private.id
  private_subnet_ids     = aws_subnet.private[*].id
  project_name           = var.project_name
  public_route_table_id  = aws_route_table.public.id
  vpc_cidr               = var.vpc_cidr
  vpc_id                 = aws_vpc.main.id
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-vpc"
  })
}

resource "aws_cloudwatch_log_group" "flow_logs" {
  kms_key_id        = var.kms_key_arn
  name              = "/aws/vpc-flow-logs/${var.project_name}-${var.environment}"
  retention_in_days = var.log_retention_in_days
  tags              = var.common_tags
}

resource "aws_flow_log" "main" {
  iam_role_arn    = aws_iam_role.flow_logs.arn
  log_destination = aws_cloudwatch_log_group.flow_logs.arn
  traffic_type    = "ALL"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-vpc-flow-log"
  })
  vpc_id = aws_vpc.main.id
}

resource "aws_iam_policy" "flow_logs" {
  name   = "${var.project_name}-${var.environment}-flow-logs-policy"
  policy = data.aws_iam_policy_document.flow_logs_policy.json
  tags   = var.common_tags
}

resource "aws_iam_role" "flow_logs" {
  assume_role_policy = data.aws_iam_policy_document.flow_logs_assume_role.json
  name               = "${var.project_name}-${var.environment}-flow-logs-role"
  tags               = var.common_tags
}

resource "aws_iam_role_policy_attachment" "flow_logs" {
  policy_arn = aws_iam_policy.flow_logs.arn
  role       = aws_iam_role.flow_logs.name
}

resource "aws_internet_gateway" "main" {
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-igw"
  })
  vpc_id = aws_vpc.main.id
}

# nosemgrep: terraform.aws.security.aws-subnet-has-public-ip-address.aws-subnet-has-public-ip-address
resource "aws_subnet" "public" {
  availability_zone       = var.availability_zones[count.index]
  cidr_block              = var.public_subnet_cidrs[count.index]
  count                   = length(var.public_subnet_cidrs)
  map_public_ip_on_launch = true
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-public-${var.availability_zones[count.index]}"
    Type = "Public"
  })
  vpc_id = aws_vpc.main.id
}

resource "aws_subnet" "private" {
  availability_zone = var.availability_zones[count.index]
  cidr_block        = var.private_subnet_cidrs[count.index]
  count             = length(var.private_subnet_cidrs)
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-private-${var.availability_zones[count.index]}"
    Type = "Private"
  })
  vpc_id = aws_vpc.main.id
}

resource "aws_eip" "nat" {
  depends_on = [aws_internet_gateway.main]
  domain     = "vpc"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-nat-eip"
  })
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  depends_on    = [aws_internet_gateway.main]
  subnet_id     = aws_subnet.public[0].id
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-nat"
  })
}

resource "aws_route_table" "public" {
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-public-rt"
  })
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
}

resource "aws_route_table" "private" {
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-private-rt"
  })
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }
}

resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  route_table_id = aws_route_table.public.id
  subnet_id      = aws_subnet.public[count.index].id
}

resource "aws_route_table_association" "private" {
  count          = length(aws_subnet.private)
  route_table_id = aws_route_table.private.id
  subnet_id      = aws_subnet.private[count.index].id
}
