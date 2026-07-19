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
  common_tags          = { Environment = "test", Project = "nest" }
  environment          = "test"
  fixtures_bucket_name = "nest-fixtures"
  kms_key_arn          = "arn:aws:kms:us-east-1:000000000000:key/1234abcd-12ab-34cd-56ef-1234567890ab"
  project_name         = "nest"
}

run "storage_integration_apply" {
  command = apply

  assert {
    condition     = can(module.fixtures_bucket.bucket.arn)
    error_message = "Fixtures bucket was not created."
  }

  assert {
    condition     = aws_iam_policy.fixtures_read_only.name == "${var.project_name}-${var.environment}-fixtures-read-only"
    error_message = "IAM policy name format is incorrect."
  }

  assert {
    condition     = aws_iam_policy.static_read_write.name == "${var.project_name}-${var.environment}-static-read-write"
    error_message = "Static IAM policy name format is incorrect."
  }

  assert {
    condition     = tolist(tolist(module.fixtures_bucket.server_side_encryption_configuration.rule)[0].apply_server_side_encryption_by_default)[0].kms_master_key_id == var.kms_key_arn
    error_message = "Fixtures bucket server-side encryption KMS key ARN is incorrect."
  }

  assert {
    condition     = tolist(tolist(module.fixtures_bucket.server_side_encryption_configuration.rule)[0].apply_server_side_encryption_by_default)[0].sse_algorithm == "aws:kms"
    error_message = "Fixtures bucket server-side encryption algorithm is not aws:kms."
  }
}
