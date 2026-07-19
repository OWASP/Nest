provider "aws" {
  access_key                  = "test"
  region                      = "us-east-1"
  s3_use_path_style           = true
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
}

variables {
  alias_name   = "alias/nest-test-integration"
  common_tags  = { Environment = "test", Project = "nest" }
  environment  = "test"
  project_name = "nest"
}

run "kms_integration_apply" {
  command = apply

  assert {
    condition     = can(aws_kms_key.main.key_id)
    error_message = "KMS key was not created."
  }

  assert {
    condition     = aws_kms_alias.main.name == var.alias_name
    error_message = "KMS alias name format is incorrect."
  }

  assert {
    condition     = aws_kms_alias.main.target_key_id == aws_kms_key.main.key_id
    error_message = "KMS alias must point to the created KMS key."
  }
}
