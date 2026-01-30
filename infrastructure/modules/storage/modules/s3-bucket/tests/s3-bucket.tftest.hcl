mock_provider "aws" {}

variables {
  bucket_name = "test-bucket"
  tags        = { Environment = "test", Project = "nest" }
}

run "test_bucket_name" {
  command = plan

  assert {
    condition     = aws_s3_bucket.this.bucket == var.bucket_name
    error_message = "Bucket name must match the bucket_name variable."
  }
}

run "test_public_access_block_all_blocked" {
  command = plan

  assert {
    condition = alltrue([
      aws_s3_bucket_public_access_block.this.block_public_acls,
      aws_s3_bucket_public_access_block.this.block_public_policy,
      aws_s3_bucket_public_access_block.this.ignore_public_acls,
      aws_s3_bucket_public_access_block.this.restrict_public_buckets
    ])
    error_message = "S3 bucket must block all public access."
  }
}

run "test_versioning_enabled" {
  command = plan

  assert {
    condition     = aws_s3_bucket_versioning.this.versioning_configuration[0].status == "Enabled"
    error_message = "S3 bucket versioning must be enabled."
  }
}

run "test_encryption_algorithm" {
  command = plan

  assert {
    condition     = one(aws_s3_bucket_server_side_encryption_configuration.this.rule).apply_server_side_encryption_by_default[0].sse_algorithm == "AES256"
    error_message = "S3 bucket must use AES256 encryption."
  }
}

run "test_lifecycle_rule_enabled" {
  command = plan

  assert {
    condition     = one(aws_s3_bucket_lifecycle_configuration.this.rule).status == "Enabled"
    error_message = "S3 lifecycle rule must be enabled."
  }
}

run "test_lifecycle_multipart_abort_days" {
  command = plan

  assert {
    condition     = one(aws_s3_bucket_lifecycle_configuration.this.rule).abort_incomplete_multipart_upload[0].days_after_initiation == 7
    error_message = "S3 lifecycle must abort incomplete multipart uploads after 7 days."
  }
}

run "test_lifecycle_noncurrent_expiration_days" {
  command = plan

  assert {
    condition     = one(aws_s3_bucket_lifecycle_configuration.this.rule).noncurrent_version_expiration[0].noncurrent_days == 30
    error_message = "S3 lifecycle must expire noncurrent versions after 30 days."
  }
}
