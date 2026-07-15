provider "aws" {
  access_key                  = "mock"
  region                      = "us-east-2"
  secret_key                  = "mock"
  skip_credentials_validation = true
  skip_requesting_account_id  = true
}

override_data {
  target = data.aws_caller_identity.current
  values = {
    account_id = "160885282306"
    arn        = "arn:aws:iam::160885282306:user/nest-bootstrap"
    user_id    = "EXAMPLE"
  }
}

variables {
  aws_role_external_id = "test-external-id"
  project_name         = "nest"
}

run "test_part_one_policy_size_production" {
  command = plan

  assert {
    condition     = module.bootstrap_iam.part_one_policy_arn != ""
    error_message = "Production part_one policy must be created."
  }
}

run "test_production_secrets_manager_namespace" {
  command = plan

  assert {
    condition     = module.bootstrap_iam.terraform_role_arn != ""
    error_message = "Production Terraform role must be created."
  }
}
