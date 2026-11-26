terraform {
  required_version = "~> 1.16.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.66.0"
    }
  }
}

data "aws_secretsmanager_secret_version" "current" {
  for_each = var.credential_names

  secret_id     = each.value
  version_stage = "AWSCURRENT"
}
