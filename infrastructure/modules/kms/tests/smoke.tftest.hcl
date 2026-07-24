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
  alias_name   = "alias/nest-staging"
  common_tags  = { Environment = "staging", Project = "nest" }
  environment  = "staging"
  project_name = "nest"
}

run "smoke_staging_kms_key" {
  command = apply

  assert {
    condition     = can(aws_kms_key.main.key_id)
    error_message = "KMS key was not created."
  }

  assert {
    condition     = aws_kms_key.main.enable_key_rotation == true
    error_message = "KMS key rotation must be enabled."
  }

  assert {
    condition     = aws_kms_alias.main.name == "alias/nest-staging"
    error_message = "KMS alias must be alias/nest-staging for staging environment."
  }

  assert {
    condition     = aws_kms_alias.main.target_key_id == aws_kms_key.main.key_id
    error_message = "KMS alias must point to the created key."
  }
}
