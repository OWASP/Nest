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

  assert {
    condition     = output.shared_data_bucket_name == null
    error_message = "Shared data bucket output must be null when create_shared_data_bucket is false."
  }
}

run "storage_integration_apply_with_shared_data_bucket" {
  command = apply

  variables {
    create_shared_data_bucket = true
  }

  assert {
    condition     = length(module.shared_data_bucket) == 1
    error_message = "Shared data bucket was not created when create_shared_data_bucket is true."
  }

  assert {
    condition     = output.shared_data_bucket_name != null
    error_message = "Shared data bucket output must be set when create_shared_data_bucket is true."
  }
}
