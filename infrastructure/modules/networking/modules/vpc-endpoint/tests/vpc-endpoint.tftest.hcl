variables {
  aws_region             = "us-east-1"
  common_tags            = { Environment = "test", Project = "nest" }
  environment            = "test"
  private_route_table_id = "rtb-private-12345"
  private_subnet_ids     = ["subnet-private-1", "subnet-private-2"]
  project_name           = "nest"
  public_route_table_id  = "rtb-public-12345"
  vpc_cidr               = "10.0.0.0/16"
  vpc_id                 = "vpc-12345678"
}

run "test_security_group_not_created_when_no_endpoint" {
  command = plan

  variables {
    create_cloudwatch_logs = false
    create_ecr_api = false
    create_ecr_dkr = false
    create_s3 = false
    create_secretsmanager = false
    create_ssm = false
  }

  assert {
    condition     = length(aws_security_group.vpc_endpoints) == 0
    error_message = "Security group should not be created when no interface endpoints are requested."
  }
}

run "test_security_group_created_with_interface_endpoint" {
  command = plan

  variables {
    create_cloudwatch_logs = true
    create_ecr_api = false
    create_ecr_dkr = false
    create_s3 = false
    create_secretsmanager = false
    create_ssm = false
  }
  assert {
    condition     = length(aws_security_group.vpc_endpoints) == 1
    error_message = "Security group should be created when any interface endpoint is created."
  }
}

run "test_security_group_allows_https_from_vpc" {
  command = plan

  variables {
    create_cloudwatch_logs = true
    create_s3 = false
  }
  assert {
    condition     = aws_security_group_rule.vpc_endpoints_ingress_https[0].from_port == 443
    error_message = "Security group must allow HTTPS (port 443)."
  }
  assert {
    condition     = aws_security_group_rule.vpc_endpoints_ingress_https[0].to_port == 443
    error_message = "Security group must allow HTTPS (port 443)."
  }
  assert {
    condition     = contains(aws_security_group_rule.vpc_endpoints_ingress_https[0].cidr_blocks, "10.0.0.0/16")
    error_message = "Security group must allow traffic from VPC CIDR."
  }
}

run "test_security_group_name_format" {
  command = plan

  variables {
    create_cloudwatch_logs = true
    create_s3 = false
  }
  assert {
    condition     = aws_security_group.vpc_endpoints[0].tags["Name"] == "nest-test-vpc-endpoints-sg"
    error_message = "Security group name must follow format: {project}-{environment}-vpc-endpoints-sg."
  }
}

run "test_cloudwatch_logs_not_created_by_default" {
  command = plan

  assert {
    condition     = length(aws_vpc_endpoint.cloudwatch_logs) == 0
    error_message = "CloudWatch Logs endpoint should not be created by default."
  }
}

run "test_cloudwatch_logs_created_when_enabled" {
  command = plan

  variables {
    create_cloudwatch_logs = true
  }

  assert {
    condition     = length(aws_vpc_endpoint.cloudwatch_logs) == 1
    error_message = "CloudWatch Logs endpoint should be created when create_cloudwatch_logs is true."
  }
  assert {
    condition     = aws_vpc_endpoint.cloudwatch_logs[0].vpc_endpoint_type == "Interface"
    error_message = "CloudWatch Logs endpoint must be Interface type."
  }
  assert {
    condition     = aws_vpc_endpoint.cloudwatch_logs[0].private_dns_enabled == true
    error_message = "CloudWatch Logs endpoint must have private DNS enabled."
  }
}

run "test_cloudwatch_logs_name_format" {
  command = plan

  variables {
    create_cloudwatch_logs = true
  }
  assert {
    condition     = aws_vpc_endpoint.cloudwatch_logs[0].tags["Name"] == "nest-test-cloudwatch-logs-endpoint"
    error_message = "CloudWatch Logs endpoint name must follow format: {project}-{environment}-cloudwatch-logs-endpoint."
  }
}

run "test_ecr_api_not_created_by_default" {
  command = plan

  assert {
    condition     = length(aws_vpc_endpoint.ecr_api) == 0
    error_message = "ECR API endpoint should not be created by default."
  }
}

run "test_ecr_api_created_when_enabled" {
  command = plan

  variables {
    create_ecr_api = true
  }
  assert {
    condition     = length(aws_vpc_endpoint.ecr_api) == 1
    error_message = "ECR API endpoint should be created when create_ecr_api is true."
  }
  assert {
    condition     = aws_vpc_endpoint.ecr_api[0].vpc_endpoint_type == "Interface"
    error_message = "ECR API endpoint must be Interface type."
  }
  assert {
    condition     = aws_vpc_endpoint.ecr_api[0].private_dns_enabled == true
    error_message = "ECR API endpoint must have private DNS enabled."
  }
}

run "test_ecr_api_name_format" {
  command = plan

  variables {
    create_ecr_api = true
  }
  assert {
    condition     = aws_vpc_endpoint.ecr_api[0].tags["Name"] == "nest-test-ecr-api-endpoint"
    error_message = "ECR API endpoint name must follow format: {project}-{environment}-ecr-api-endpoint."
  }
}

run "test_ecr_dkr_not_created_by_default" {
  command = plan

  assert {
    condition     = length(aws_vpc_endpoint.ecr_dkr) == 0
    error_message = "ECR DKR endpoint should not be created by default."
  }
}

run "test_ecr_dkr_created_when_enabled" {
  command = plan

  variables {
    create_ecr_dkr = true
  }
  assert {
    condition     = length(aws_vpc_endpoint.ecr_dkr) == 1
    error_message = "ECR DKR endpoint should be created when create_ecr_dkr is true."
  }
  assert {
    condition     = aws_vpc_endpoint.ecr_dkr[0].vpc_endpoint_type == "Interface"
    error_message = "ECR DKR endpoint must be Interface type."
  }
  assert {
    condition     = aws_vpc_endpoint.ecr_dkr[0].private_dns_enabled == true
    error_message = "ECR DKR endpoint must have private DNS enabled."
  }
}

run "test_ecr_dkr_name_format" {
  command = plan

  variables {
    create_ecr_dkr = true
  }
  assert {
    condition     = aws_vpc_endpoint.ecr_dkr[0].tags["Name"] == "nest-test-ecr-dkr-endpoint"
    error_message = "ECR DKR endpoint name must follow format: {project}-{environment}-ecr-dkr-endpoint."
  }
}

run "test_s3_created_by_default" {
  command = plan

  assert {
    condition     = length(aws_vpc_endpoint.s3) == 1
    error_message = "S3 endpoint should be created by default."
  }
}

run "test_s3_is_gateway_type" {
  command = plan

  assert {
    condition     = aws_vpc_endpoint.s3[0].vpc_endpoint_type == "Gateway"
    error_message = "S3 endpoint must be Gateway type."
  }
}

run "test_s3_name_format" {
  command = plan

  assert {
    condition     = aws_vpc_endpoint.s3[0].tags["Name"] == "nest-test-s3-endpoint"
    error_message = "S3 endpoint name must follow format: {project}-{environment}-s3-endpoint."
  }
}

run "test_s3_route_table_associations_created" {
  command = plan

  assert {
    condition     = length(aws_vpc_endpoint_route_table_association.s3_private) == 1
    error_message = "S3 private route table association should be created when S3 endpoint exists."
  }
  assert {
    condition     = length(aws_vpc_endpoint_route_table_association.s3_public) == 1
    error_message = "S3 public route table association should be created when S3 endpoint exists."
  }
}

run "test_secretsmanager_not_created_by_default" {
  command = plan

  assert {
    condition     = length(aws_vpc_endpoint.secretsmanager) == 0
    error_message = "Secrets Manager endpoint should not be created by default."
  }
}

run "test_secretsmanager_created_when_enabled" {
  command = plan

  variables {
    create_secretsmanager = true
  }
  assert {
    condition     = length(aws_vpc_endpoint.secretsmanager) == 1
    error_message = "Secrets Manager endpoint should be created when create_secretsmanager is true."
  }
  assert {
    condition     = aws_vpc_endpoint.secretsmanager[0].vpc_endpoint_type == "Interface"
    error_message = "Secrets Manager endpoint must be Interface type."
  }
  assert {
    condition     = aws_vpc_endpoint.secretsmanager[0].private_dns_enabled == true
    error_message = "Secrets Manager endpoint must have private DNS enabled."
  }
}

run "test_secretsmanager_name_format" {
  command = plan

  variables {
    create_secretsmanager = true
  }

  assert {
    condition     = aws_vpc_endpoint.secretsmanager[0].tags["Name"] == "nest-test-secretsmanager-endpoint"
    error_message = "Secrets Manager endpoint name must follow format: {project}-{environment}-secretsmanager-endpoint."
  }
}

run "test_ssm_not_created_by_default" {
  command = plan

  assert {
    condition     = length(aws_vpc_endpoint.ssm) == 0
    error_message = "SSM endpoint should not be created by default."
  }
}

run "test_ssm_created_when_enabled" {
  command = plan

  variables {
    create_ssm = true
  }
  assert {
    condition     = length(aws_vpc_endpoint.ssm) == 1
    error_message = "SSM endpoint should be created when create_ssm is true."
  }
  assert {
    condition     = aws_vpc_endpoint.ssm[0].vpc_endpoint_type == "Interface"
    error_message = "SSM endpoint must be Interface type."
  }
  assert {
    condition     = aws_vpc_endpoint.ssm[0].private_dns_enabled == true
    error_message = "SSM endpoint must have private DNS enabled."
  }
}

run "test_ssm_name_format" {
  command = plan

  variables {
    create_ssm = true
  }
  assert {
    condition     = aws_vpc_endpoint.ssm[0].tags["Name"] == "nest-test-ssm-endpoint"
    error_message = "SSM endpoint name must follow format: {project}-{environment}-ssm-endpoint."
  }
}
