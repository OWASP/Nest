terraform {
  required_version = "~> 1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.53.0"
    }
  }
}

module "bootstrap_iam" {
  source = "../modules/bootstrap-iam"

  aws_region              = var.aws_region
  aws_role_external_id    = var.aws_role_external_id
  environment             = "staging"
  project_name            = var.project_name
  shared_data_bucket_name = var.shared_data_bucket_name
}
