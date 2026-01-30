variables {
  common_tags          = { Environment = "test", Project = "nest" }
  environment          = "test"
  fixtures_bucket_name = "nest-fixtures"
  project_name         = "nest"
  zappa_bucket_name    = "nest-zappa"
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

run "test_zappa_bucket_name" {
  command = plan

  override_resource {
    target          = random_id.suffix
    override_during = plan
    values = {
      hex = "abcd1234"
    }
  }

  assert {
    condition     = module.zappa_bucket.bucket.bucket == "${var.zappa_bucket_name}-abcd1234"
    error_message = "Zappa bucket name must follow format: {zappa_bucket_name}-{suffix}."
  }
}

run "test_iam_policy_name_format" {
  command = plan

  assert {
    condition     = aws_iam_policy.fixtures_read_only.name == "${var.project_name}-${var.environment}-fixtures-read-only"
    error_message = "IAM policy name must follow format: {project}-{environment}-fixtures-read-only."
  }
}
