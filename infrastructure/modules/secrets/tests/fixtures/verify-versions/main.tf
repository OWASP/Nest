terraform {
  required_version = "~> 1.16.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.66.0"
    }
  }
}

variable "credential_names" {
  description = "Names of the PR1 secrets to read back after cutover."
  type        = map(string)
}

data "aws_secretsmanager_secret_version" "current" {
  for_each = var.credential_names

  secret_id     = each.value
  version_stage = "AWSCURRENT"
}

output "credential_versions" {
  description = "Actual AWSCURRENT version identities and fake values after handoff."
  sensitive   = true
  value = { for name, version in data.aws_secretsmanager_secret_version.current : name => {
    version_id = version.version_id
    value      = version.secret_string
  } }
}
