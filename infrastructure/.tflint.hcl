plugin "aws" {
  enabled = true
  version = "0.44.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}

plugin "terraform" {
  enabled = true
  version = "0.13.0"
  source  = "github.com/terraform-linters/tflint-ruleset-terraform"
}

rule "aws_resource_missing_tags" {
  enabled = false
}

rule "terraform_documented_outputs" {
  enabled = true
}

rule "terraform_documented_variables" {
  enabled = true
}

rule "terraform_module_pinned_source" {
  enabled = true
  style   = "semver"
}

rule "terraform_naming_convention" {
  enabled = true
  format  = "snake_case"
}

rule "terraform_required_providers" {
  enabled = true
  source  = true
  # Child modules declare provider source only; roots pin versions in live/state/bootstrap.
  version = false
}

rule "terraform_required_version" {
  enabled = true
}

rule "terraform_typed_variables" {
  enabled = true
}
