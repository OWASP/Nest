mock_provider "aws" {}

variables {
  common_tags  = { Environment = "test", Project = "nest" }
  environment  = "test"
  project_name = "nest"
}

run "test_alias_name_format" {
  command = plan

  assert {
    condition     = aws_kms_alias.main.name == "alias/${var.project_name}-${var.environment}"
    error_message = "KMS alias must follow format: alias/{project}-{environment}."
  }
}

run "test_cloudwatch_logs_policy_statement_exists" {
  command = plan

  assert {
    condition     = can(regex("AllowCloudWatchLogs", data.aws_iam_policy_document.key_policy.json))
    error_message = "Key policy must include CloudWatch Logs permissions."
  }
}

run "test_deletion_window" {
  command = plan

  variables {
    deletion_window_in_days = 14
  }

  assert {
    condition     = aws_kms_key.main.deletion_window_in_days == 14
    error_message = "KMS key must use deletion window when provided."
  }
}

run "test_default_deletion_window" {
  command = plan

  assert {
    condition     = aws_kms_key.main.deletion_window_in_days == 30
    error_message = "KMS key deletion window must default to 30 days."
  }
}

run "test_iam_root_policy_statement_exists" {
  command = plan

  assert {
    condition     = can(regex("EnableIAMUserPermissions", data.aws_iam_policy_document.key_policy.json))
    error_message = "Key policy must include IAM root permissions."
  }
}

run "test_key_rotation_enabled" {
  command = plan

  assert {
    condition     = aws_kms_key.main.enable_key_rotation == true
    error_message = "Key rotation must be enabled."
  }
}

run "test_key_spec_is_symmetric" {
  command = plan

  assert {
    condition     = aws_kms_key.main.customer_master_key_spec == "SYMMETRIC_DEFAULT"
    error_message = "KMS key must use SYMMETRIC_DEFAULT key spec."
  }
}

run "test_key_usage_is_encrypt_decrypt" {
  command = plan

  assert {
    condition     = aws_kms_key.main.key_usage == "ENCRYPT_DECRYPT"
    error_message = "KMS key usage must be ENCRYPT_DECRYPT."
  }
}
