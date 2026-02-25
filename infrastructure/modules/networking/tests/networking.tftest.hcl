mock_provider "aws" {}

variables {
  availability_zones                  = ["us-east-2a", "us-east-2b", "us-east-2c"]
  aws_region                          = "us-east-2"
  common_tags                         = { Environment = "test", Project = "nest" }
  create_vpc_cloudwatch_logs_endpoint = false
  create_vpc_ecr_api_endpoint         = false
  create_vpc_ecr_dkr_endpoint         = false
  create_vpc_s3_endpoint              = false
  create_vpc_secretsmanager_endpoint  = false
  create_vpc_ssm_endpoint             = false
  environment                         = "test"
  kms_key_arn                         = "arn:aws:kms:us-east-2:123456789012:key/12345678-1234-1234-1234-123456789012"
  log_retention_in_days               = 90
  private_subnet_cidrs                = ["10.0.3.0/24", "10.0.4.0/24", "10.0.5.0/24"]
  project_name                        = "nest"
  public_subnet_cidrs                 = ["10.0.1.0/24", "10.0.2.0/24", "10.0.6.0/24"]
  vpc_cidr                            = "10.0.0.0/16"
}

run "test_vpc_name_format" {
  command = plan

  assert {
    condition     = aws_vpc.main.tags["Name"] == "${var.project_name}-${var.environment}-vpc"
    error_message = "VPC name must follow format: {project}-{environment}-vpc."
  }
}

run "test_vpc_cidr_block" {
  command = plan

  assert {
    condition     = aws_vpc.main.cidr_block == var.vpc_cidr
    error_message = "VPC CIDR block must match provided value."
  }
}

run "test_vpc_dns_hostnames_enabled" {
  command = plan

  assert {
    condition     = aws_vpc.main.enable_dns_hostnames == true
    error_message = "VPC DNS hostnames must be enabled."
  }
}

run "test_vpc_dns_support_enabled" {
  command = plan

  assert {
    condition     = aws_vpc.main.enable_dns_support == true
    error_message = "VPC DNS support must be enabled."
  }
}

run "test_public_subnet_name_format" {
  command = plan

  assert {
    condition = alltrue([
      for i, subnet in aws_subnet.public :
      subnet.tags["Name"] == "${var.project_name}-${var.environment}-public-${var.availability_zones[i]}"
    ])
    error_message = "Public subnet names must follow format: {project}-{environment}-public-{az}."
  }
}

run "test_public_subnets_in_correct_availability_zones" {
  command = plan

  assert {
    condition     = alltrue([for i, subnet in aws_subnet.public : subnet.availability_zone == var.availability_zones[i]])
    error_message = "Public subnets must be in correct availability zones."
  }
}

run "test_public_subnets_count" {
  command = plan

  assert {
    condition     = length(aws_subnet.public) == length(var.public_subnet_cidrs)
    error_message = "Number of public subnets must match provided CIDRs."
  }
}

run "test_public_subnets_map_public_ip" {
  command = plan

  assert {
    condition     = alltrue([for subnet in aws_subnet.public : subnet.map_public_ip_on_launch == true])
    error_message = "Public subnets must auto-assign public IPs."
  }
}

run "test_private_subnet_name_format" {
  command = plan

  assert {
    condition = alltrue([
      for i, subnet in aws_subnet.private :
      subnet.tags["Name"] == "${var.project_name}-${var.environment}-private-${var.availability_zones[i]}"
    ])
    error_message = "Private subnet names must follow format: {project}-{environment}-private-{az}."
  }
}

run "test_private_subnets_in_correct_availability_zones" {
  command = plan

  assert {
    condition     = alltrue([for i, subnet in aws_subnet.private : subnet.availability_zone == var.availability_zones[i]])
    error_message = "Private subnets must be in correct availability zones."
  }
}

run "test_private_subnets_count" {
  command = plan

  assert {
    condition     = length(aws_subnet.private) == length(var.private_subnet_cidrs)
    error_message = "Number of private subnets must match provided CIDRs."
  }
}

run "test_private_subnets_no_public_ip" {
  command = plan

  assert {
    condition     = alltrue([for subnet in aws_subnet.private : subnet.map_public_ip_on_launch != true])
    error_message = "Private subnets must not auto-assign public IPs."
  }
}

run "test_internet_gateway_name_format" {
  command = plan

  assert {
    condition     = aws_internet_gateway.main.tags["Name"] == "${var.project_name}-${var.environment}-igw"
    error_message = "Internet gateway name must follow format: {project}-{environment}-igw."
  }
}

run "test_nat_eip_name_format" {
  command = plan

  assert {
    condition     = aws_eip.nat.tags["Name"] == "${var.project_name}-${var.environment}-nat-eip"
    error_message = "NAT EIP name must follow format: {project}-{environment}-nat-eip."
  }
}

run "test_nat_gateway_name_format" {
  command = plan

  assert {
    condition     = aws_nat_gateway.main.tags["Name"] == "${var.project_name}-${var.environment}-nat"
    error_message = "NAT gateway name must follow format: {project}-{environment}-nat."
  }
}

run "test_eip_domain_is_vpc" {
  command = plan

  assert {
    condition     = aws_eip.nat.domain == "vpc"
    error_message = "NAT EIP domain must be VPC."
  }
}

run "test_public_route_table_name_format" {
  command = plan

  assert {
    condition     = aws_route_table.public.tags["Name"] == "${var.project_name}-${var.environment}-public-rt"
    error_message = "Public route table name must follow format: {project}-{environment}-public-rt."
  }
}

run "test_public_route_table_associations_count" {
  command = plan

  assert {
    condition     = length(aws_route_table_association.public) == length(aws_subnet.public)
    error_message = "All public subnets must be associated with public route table."
  }
}

run "test_private_route_table_name_format" {
  command = plan

  assert {
    condition     = aws_route_table.private.tags["Name"] == "${var.project_name}-${var.environment}-private-rt"
    error_message = "Private route table name must follow format: {project}-{environment}-private-rt."
  }
}

run "test_private_route_table_associations_count" {
  command = plan

  assert {
    condition     = length(aws_route_table_association.private) == length(aws_subnet.private)
    error_message = "All private subnets must be associated with private route table."
  }
}

run "test_cloudwatch_log_group_name_format" {
  command = plan

  assert {
    condition     = aws_cloudwatch_log_group.flow_logs.name == "/aws/vpc-flow-logs/${var.project_name}-${var.environment}"
    error_message = "CloudWatch log group name must follow format: /aws/vpc-flow-logs/{project}-{environment}."
  }
}

run "test_flow_log_name_format" {
  command = plan

  assert {
    condition     = aws_flow_log.main.tags["Name"] == "${var.project_name}-${var.environment}-vpc-flow-log"
    error_message = "Flow log name must follow format: {project}-{environment}-vpc-flow-log."
  }
}

run "test_flow_logs_log_group_retention" {
  command = plan

  assert {
    condition     = aws_cloudwatch_log_group.flow_logs.retention_in_days == var.log_retention_in_days
    error_message = "Flow logs log group must have correct retention."
  }
}

run "test_flow_logs_log_group_encrypted" {
  command = plan

  assert {
    condition     = aws_cloudwatch_log_group.flow_logs.kms_key_id == var.kms_key_arn
    error_message = "Flow logs log group must be encrypted with provided KMS key."
  }
}

run "test_vpc_endpoint_module_not_created_by_default" {
  command = plan

  assert {
    condition     = length(module.vpc_endpoint) == 0
    error_message = "VPC endpoint module must not be created when all endpoints are disabled."
  }
}

run "test_vpc_endpoint_module_created_when_enabled" {
  command = plan

  variables {
    create_vpc_s3_endpoint = true
  }
  assert {
    condition     = length(module.vpc_endpoint) == 1
    error_message = "VPC endpoint module must be created when at least one endpoint is enabled."
  }
}
