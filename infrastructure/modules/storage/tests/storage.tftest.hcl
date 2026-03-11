mock_provider "aws" {}

variables {
  common_tags          = { Environment = "test", Project = "nest" }
  environment          = "test"
  fixtures_bucket_name = "nest-fixtures"
  project_name         = "nest"
}

run "test_fixtures_bucket_name" {
  command = plan

  override_resource {
    target          = random_id.suffix
    override_during = plan
    values = {
      hex = "abcd1234"
    }
  }

  assert {
    condition     = module.fixtures_bucket.bucket.bucket == "${var.fixtures_bucket_name}-abcd1234"
    error_message = "Fixtures bucket name must follow format: {fixtures_bucket_name}-{suffix}."
  }
}

run "test_iam_policy_name_format" {
  command = plan

  assert {
    condition     = aws_iam_policy.fixtures_read_only.name == "${var.project_name}-${var.environment}-fixtures-read-only"
    error_message = "IAM policy name must follow format: {project}-{environment}-fixtures-read-only."
  }
}

run "test_static_bucket_name" {
  command = plan

  override_resource {
    target          = random_id.suffix
    override_during = plan
    values = {
      hex = "abcd1234"
    }
  }

  assert {
    condition     = module.static_bucket.bucket.bucket == "${var.project_name}-${var.environment}-static-abcd1234"
    error_message = "Static bucket name must follow format: {project}-{environment}-static-{suffix}."
  }
}

run "test_static_iam_policy_name_format" {
  command = plan

  assert {
    condition     = aws_iam_policy.static_read_write.name == "${var.project_name}-${var.environment}-static-read-write"
    error_message = "Static IAM policy name must follow format: {project}-{environment}-static-read-write."
  }
}
