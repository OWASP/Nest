terraform {
  required_version = "~> 1.15.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.53.0"
    }
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "main" {
  count = 2

  availability_zone = data.aws_availability_zones.available.names[count.index]
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  vpc_id            = aws_vpc.main.id
}

resource "aws_security_group" "app" {
  count = 3

  name   = "nest-test-app-${count.index}"
  vpc_id = aws_vpc.main.id
}

resource "aws_kms_key" "main" {
  description = "Test key for the observability integration tests."
}

output "app_security_group_ids" {
  value = aws_security_group.app[*].id
}

output "kms_key_arn" {
  value = aws_kms_key.main.arn
}

output "subnet_ids" {
  value = aws_subnet.main[*].id
}

output "vpc_id" {
  value = aws_vpc.main.id
}
