provider "aws" {
  access_key                  = "mock"
  region                      = "us-east-2"
  secret_key                  = "mock"
  skip_credentials_validation = true
  skip_requesting_account_id  = true
}

override_data {
  target = module.bootstrap_iam.data.aws_caller_identity.current
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

run "test_production_policy_names" {
  command = plan

  assert {
    condition = alltrue([
      module.bootstrap_iam.part_one_policy_name == "nest-production-part-one-terraform",
      module.bootstrap_iam.part_two_policy_name == "nest-production-part-two-terraform",
    ])
    error_message = "Production bootstrap must only create production policies."
  }
}

run "test_production_terraform_role_name" {
  command = plan

  assert {
    condition     = module.bootstrap_iam.terraform_role_name == "nest-production-terraform"
    error_message = "Production bootstrap must only create the production Terraform role."
  }
}
