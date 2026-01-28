variables {
  common_tags        = { Environment = "test", Project = "nest" }
  environment        = "test"
  private_subnet_ids = ["subnet-private-1", "subnet-private-2"]
  project_name       = "nest"
  public_subnet_ids  = ["subnet-public-1", "subnet-public-2"]
  vpc_cidr           = "10.0.0.0/16"
  vpc_id             = "vpc-12345678"
}

run "test_private_nacl_created" {
  command = plan

  assert {
    condition     = aws_network_acl.private.vpc_id != ""
    error_message = "Private NACL should be created."
  }
}

run "test_private_nacl_name_format" {
  command = plan

  assert {
    condition     = aws_network_acl.private.tags["Name"] == "nest-test-private-nacl"
    error_message = "Private NACL name must follow format: {project}-{environment}-private-nacl."
  }
}

run "test_public_nacl_created" {
  command = plan

  assert {
    condition     = aws_network_acl.public.vpc_id != ""
    error_message = "Public NACL should be created."
  }
}

run "test_public_nacl_name_format" {
  command = plan

  assert {
    condition     = aws_network_acl.public.tags["Name"] == "nest-test-public-nacl"
    error_message = "Public NACL name must follow format: {project}-{environment}-public-nacl."
  }
}

run "test_private_nacl_associations_count" {
  command = plan

  assert {
    condition     = length(aws_network_acl_association.private) == 2
    error_message = "Private NACL should have 2 subnet associations."
  }
}

run "test_public_nacl_associations_count" {
  command = plan

  assert {
    condition     = length(aws_network_acl_association.public) == 2
    error_message = "Public NACL should have 2 subnet associations."
  }
}

run "test_private_inbound_ephemeral_rule" {
  command = plan

  assert {
    condition     = aws_network_acl_rule.private_inbound_ephemeral.from_port == 1024
    error_message = "Private NACL ephemeral inbound rule must start at port 1024."
  }
  assert {
    condition     = aws_network_acl_rule.private_inbound_ephemeral.to_port == 65535
    error_message = "Private NACL ephemeral inbound rule must end at port 65535."
  }
  assert {
    condition     = aws_network_acl_rule.private_inbound_ephemeral.protocol == "tcp"
    error_message = "Private NACL ephemeral inbound rule must use TCP protocol."
  }
  assert {
    condition     = aws_network_acl_rule.private_inbound_ephemeral.rule_action == "allow"
    error_message = "Private NACL ephemeral inbound rule must allow traffic."
  }
  assert {
    condition     = aws_network_acl_rule.private_inbound_ephemeral.cidr_block == "0.0.0.0/0"
    error_message = "Private NACL ephemeral inbound rule must allow from any source."
  }
  assert {
    condition     = aws_network_acl_rule.private_inbound_ephemeral.rule_number == 100
    error_message = "Private NACL ephemeral inbound rule number must be 100."
  }
}

run "test_private_inbound_https_rule" {
  command = plan

  assert {
    condition     = aws_network_acl_rule.private_inbound_https.from_port == 443
    error_message = "Private NACL HTTPS inbound rule must use port 443."
  }
  assert {
    condition     = aws_network_acl_rule.private_inbound_https.to_port == 443
    error_message = "Private NACL HTTPS inbound rule must use port 443."
  }
  assert {
    condition     = aws_network_acl_rule.private_inbound_https.protocol == "tcp"
    error_message = "Private NACL HTTPS inbound rule must use TCP protocol."
  }
  assert {
    condition     = aws_network_acl_rule.private_inbound_https.rule_action == "allow"
    error_message = "Private NACL HTTPS inbound rule must allow traffic."
  }
  assert {
    condition     = aws_network_acl_rule.private_inbound_https.cidr_block == "10.0.0.0/16"
    error_message = "Private NACL HTTPS inbound rule must allow from VPC CIDR."
  }
  assert {
    condition     = aws_network_acl_rule.private_inbound_https.rule_number == 110
    error_message = "Private NACL HTTPS inbound rule number must be 110."
  }
}

run "test_private_inbound_postgres_rule" {
  command = plan

  assert {
    condition     = aws_network_acl_rule.private_inbound_postgres.from_port == 5432
    error_message = "Private NACL Postgres inbound rule must use port 5432."
  }
  assert {
    condition     = aws_network_acl_rule.private_inbound_postgres.to_port == 5432
    error_message = "Private NACL Postgres inbound rule must use port 5432."
  }
  assert {
    condition     = aws_network_acl_rule.private_inbound_postgres.protocol == "tcp"
    error_message = "Private NACL Postgres inbound rule must use TCP protocol."
  }
  assert {
    condition     = aws_network_acl_rule.private_inbound_postgres.rule_action == "allow"
    error_message = "Private NACL Postgres inbound rule must allow traffic."
  }
  assert {
    condition     = aws_network_acl_rule.private_inbound_postgres.cidr_block == "10.0.0.0/16"
    error_message = "Private NACL Postgres inbound rule must allow from VPC CIDR."
  }
  assert {
    condition     = aws_network_acl_rule.private_inbound_postgres.rule_number == 120
    error_message = "Private NACL Postgres inbound rule number must be 120."
  }
}

run "test_private_inbound_redis_rule" {
  command = plan

  assert {
    condition     = aws_network_acl_rule.private_inbound_redis.from_port == 6379
    error_message = "Private NACL Redis inbound rule must use port 6379."
  }
  assert {
    condition     = aws_network_acl_rule.private_inbound_redis.to_port == 6379
    error_message = "Private NACL Redis inbound rule must use port 6379."
  }
  assert {
    condition     = aws_network_acl_rule.private_inbound_redis.protocol == "tcp"
    error_message = "Private NACL Redis inbound rule must use TCP protocol."
  }
  assert {
    condition     = aws_network_acl_rule.private_inbound_redis.rule_action == "allow"
    error_message = "Private NACL Redis inbound rule must allow traffic."
  }
  assert {
    condition     = aws_network_acl_rule.private_inbound_redis.cidr_block == "10.0.0.0/16"
    error_message = "Private NACL Redis inbound rule must allow from VPC CIDR."
  }
  assert {
    condition     = aws_network_acl_rule.private_inbound_redis.rule_number == 130
    error_message = "Private NACL Redis inbound rule number must be 130."
  }
}

run "test_private_outbound_all_rule" {
  command = plan

  assert {
    condition     = aws_network_acl_rule.private_outbound_all.egress == true
    error_message = "Private NACL outbound rule must be egress."
  }
  assert {
    condition     = aws_network_acl_rule.private_outbound_all.protocol == "-1"
    error_message = "Private NACL outbound rule must allow all protocols."
  }
  assert {
    condition     = aws_network_acl_rule.private_outbound_all.rule_action == "allow"
    error_message = "Private NACL outbound rule must allow traffic."
  }
  assert {
    condition     = aws_network_acl_rule.private_outbound_all.cidr_block == "0.0.0.0/0"
    error_message = "Private NACL outbound rule must allow to any destination."
  }
  assert {
    condition     = aws_network_acl_rule.private_outbound_all.rule_number == 100
    error_message = "Private NACL outbound rule number must be 100."
  }
}

run "test_public_inbound_ephemeral_rule" {
  command = plan

  assert {
    condition     = aws_network_acl_rule.public_inbound_ephemeral.from_port == 1024
    error_message = "Public NACL ephemeral inbound rule must start at port 1024."
  }
  assert {
    condition     = aws_network_acl_rule.public_inbound_ephemeral.to_port == 65535
    error_message = "Public NACL ephemeral inbound rule must end at port 65535."
  }
  assert {
    condition     = aws_network_acl_rule.public_inbound_ephemeral.protocol == "tcp"
    error_message = "Public NACL ephemeral inbound rule must use TCP protocol."
  }
  assert {
    condition     = aws_network_acl_rule.public_inbound_ephemeral.rule_action == "allow"
    error_message = "Public NACL ephemeral inbound rule must allow traffic."
  }
  assert {
    condition     = aws_network_acl_rule.public_inbound_ephemeral.cidr_block == "0.0.0.0/0"
    error_message = "Public NACL ephemeral inbound rule must allow from any source."
  }
  assert {
    condition     = aws_network_acl_rule.public_inbound_ephemeral.rule_number == 100
    error_message = "Public NACL ephemeral inbound rule number must be 100."
  }
}

run "test_public_inbound_http_rule" {
  command = plan

  assert {
    condition     = aws_network_acl_rule.public_inbound_http.from_port == 80
    error_message = "Public NACL HTTP inbound rule must use port 80."
  }
  assert {
    condition     = aws_network_acl_rule.public_inbound_http.to_port == 80
    error_message = "Public NACL HTTP inbound rule must use port 80."
  }
  assert {
    condition     = aws_network_acl_rule.public_inbound_http.protocol == "tcp"
    error_message = "Public NACL HTTP inbound rule must use TCP protocol."
  }
  assert {
    condition     = aws_network_acl_rule.public_inbound_http.rule_action == "allow"
    error_message = "Public NACL HTTP inbound rule must allow traffic."
  }
  assert {
    condition     = aws_network_acl_rule.public_inbound_http.cidr_block == "0.0.0.0/0"
    error_message = "Public NACL HTTP inbound rule must allow from any source."
  }
  assert {
    condition     = aws_network_acl_rule.public_inbound_http.rule_number == 110
    error_message = "Public NACL HTTP inbound rule number must be 110."
  }
}

run "test_public_inbound_https_rule" {
  command = plan

  assert {
    condition     = aws_network_acl_rule.public_inbound_https.from_port == 443
    error_message = "Public NACL HTTPS inbound rule must use port 443."
  }
  assert {
    condition     = aws_network_acl_rule.public_inbound_https.to_port == 443
    error_message = "Public NACL HTTPS inbound rule must use port 443."
  }
  assert {
    condition     = aws_network_acl_rule.public_inbound_https.protocol == "tcp"
    error_message = "Public NACL HTTPS inbound rule must use TCP protocol."
  }
  assert {
    condition     = aws_network_acl_rule.public_inbound_https.rule_action == "allow"
    error_message = "Public NACL HTTPS inbound rule must allow traffic."
  }
  assert {
    condition     = aws_network_acl_rule.public_inbound_https.cidr_block == "0.0.0.0/0"
    error_message = "Public NACL HTTPS inbound rule must allow from any source."
  }
  assert {
    condition     = aws_network_acl_rule.public_inbound_https.rule_number == 120
    error_message = "Public NACL HTTPS inbound rule number must be 120."
  }
}

run "test_public_outbound_all_rule" {
  command = plan

  assert {
    condition     = aws_network_acl_rule.public_outbound_all.egress == true
    error_message = "Public NACL outbound rule must be egress."
  }
  assert {
    condition     = aws_network_acl_rule.public_outbound_all.protocol == "-1"
    error_message = "Public NACL outbound rule must allow all protocols."
  }
  assert {
    condition     = aws_network_acl_rule.public_outbound_all.rule_action == "allow"
    error_message = "Public NACL outbound rule must allow traffic."
  }
  assert {
    condition     = aws_network_acl_rule.public_outbound_all.cidr_block == "0.0.0.0/0"
    error_message = "Public NACL outbound rule must allow to any destination."
  }
  assert {
    condition     = aws_network_acl_rule.public_outbound_all.rule_number == 100
    error_message = "Public NACL outbound rule number must be 100."
  }
}
