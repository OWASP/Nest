provider "aws" {
  access_key                  = "test"
  region                      = "us-east-1"
  s3_use_path_style           = true
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    iam = "http://localhost:4566"
    kms = "http://localhost:4566"
    s3  = "http://localhost:4566"
    sts = "http://localhost:4566"
  }
}

variables {
  common_tags          = { Environment = "staging", Project = "nest" }
  environment          = "staging"
  fixtures_bucket_name = "nest-fixtures"
  kms_key_arn          = "arn:aws:kms:us-east-1:000000000000:key/1234abcd-12ab-34cd-56ef-1234567890ab"
  project_name         = "nest"
}

run "smoke_staging_storage" {
  command = apply

  assert {
    condition     = startswith(module.fixtures_bucket.bucket.id, "nest-fixtures-")
    error_message = "Fixtures bucket name must start with nest-fixtures-."
  }

  assert {
    condition     = can(module.fixtures_bucket.arn)
    error_message = "Fixtures bucket ARN must exist."
  }

  assert {
    condition     = aws_iam_policy.fixtures_read_only.name == "nest-staging-fixtures-read-only"
    error_message = "Fixtures IAM policy must be nest-staging-fixtures-read-only."
  }

  assert {
    condition     = aws_iam_policy.static_read_write.name == "nest-staging-static-read-write"
    error_message = "Static IAM policy must be nest-staging-static-read-write."
  }

  assert {
    condition     = startswith(module.static_bucket.bucket.id, "nest-staging-static-")
    error_message = "Static bucket name must start with nest-staging-static-."
  }
}
