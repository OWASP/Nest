mock_provider "aws" {}

variables {
  bucket_name            = "test-owasp-nest-shared-data"
  common_tags            = { Environment = "test", Project = "nest" }
  public_read_object_key = "nest.dump"
}

run "test_bucket_name" {
  command = plan

  assert {
    condition     = aws_s3_bucket.nest_shared_data.bucket == var.bucket_name
    error_message = "Bucket name must match the bucket_name variable."
  }
}

run "test_public_access_block_allows_anonymous_read_via_policy" {
  command = plan

  assert {
    condition = (
      aws_s3_bucket_public_access_block.nest_shared_data.block_public_acls &&
      !aws_s3_bucket_public_access_block.nest_shared_data.block_public_policy &&
      aws_s3_bucket_public_access_block.nest_shared_data.ignore_public_acls &&
      !aws_s3_bucket_public_access_block.nest_shared_data.restrict_public_buckets
    )
    error_message = "Public access block must allow a bucket policy while blocking ACL-based public access."
  }
}

run "test_versioning_enabled" {
  command = plan

  assert {
    condition     = aws_s3_bucket_versioning.nest_shared_data.versioning_configuration[0].status == "Enabled"
    error_message = "S3 bucket versioning must be enabled."
  }
}

run "test_encryption_algorithm" {
  command = plan

  assert {
    condition     = one(aws_s3_bucket_server_side_encryption_configuration.nest_shared_data.rule).apply_server_side_encryption_by_default[0].sse_algorithm == "AES256"
    error_message = "S3 bucket must use SSE-S3 (AES256) encryption."
  }
}

run "test_bucket_policy_includes_public_read_and_https_deny" {
  command = plan

  # Policy JSON embeds the bucket ARN; override ARN so the policy string is known during plan.
  override_resource {
    target          = aws_s3_bucket.nest_shared_data
    override_during = plan
    values = {
      arn = "arn:aws:s3:::test-owasp-nest-shared-data"
      id  = "test-owasp-nest-shared-data"
    }
  }

  assert {
    condition = alltrue([
      strcontains(aws_s3_bucket_policy.nest_shared_data.policy, "AllowPublicReadNestDump"),
      strcontains(aws_s3_bucket_policy.nest_shared_data.policy, "HTTPSOnly"),
      strcontains(aws_s3_bucket_policy.nest_shared_data.policy, "aws:SecureTransport"),
      strcontains(aws_s3_bucket_policy.nest_shared_data.policy, var.public_read_object_key),
    ])
    error_message = "Bucket policy must allow public GetObject on the configured key and deny insecure transport."
  }
}
