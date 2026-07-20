provider "aws" {
  access_key                  = "test"
  region                      = "us-east-2"
  s3_use_path_style           = true
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
}

variables {
  aws_role_external_id = "localstack-staging-external-id"
  environment          = "staging"
  project_name         = "nest"
}

run "bootstrap_integration_apply_staging" {
  command = apply

  assert {
    condition     = aws_iam_role.terraform.name == "${var.project_name}-${var.environment}-terraform"
    error_message = "IAM role name format is incorrect for staging."
  }

  assert {
    condition     = aws_iam_policy.part_one.name == "${var.project_name}-${var.environment}-part-one-terraform"
    error_message = "IAM policy part-one name format is incorrect for staging."
  }

  assert {
    condition     = aws_iam_policy.part_two.name == "${var.project_name}-${var.environment}-part-two-terraform"
    error_message = "IAM policy part-two name format is incorrect for staging."
  }

  assert {
    condition     = aws_iam_role_policy_attachment.attach_part_one.role == aws_iam_role.terraform.name
    error_message = "IAM policy part-one is not attached to the role in staging."
  }

  assert {
    condition     = aws_iam_role_policy_attachment.attach_part_two.role == aws_iam_role.terraform.name
    error_message = "IAM policy part-two is not attached to the role in staging."
  }

  assert {
    condition     = output.terraform_role_arn == aws_iam_role.terraform.arn
    error_message = "The terraform_role_arn output does not match the created role's ARN in staging."
  }
}

run "bootstrap_integration_apply_production" {
  command = apply

  variables {
    aws_role_external_id = "localstack-production-external-id"
    environment          = "production"
  }

  assert {
    condition     = aws_iam_role.terraform.name == "${var.project_name}-${var.environment}-terraform"
    error_message = "IAM role name format is incorrect for production."
  }

  assert {
    condition     = aws_iam_policy.part_one.name == "${var.project_name}-${var.environment}-part-one-terraform"
    error_message = "IAM policy part-one name format is incorrect for production."
  }

  assert {
    condition     = aws_iam_policy.part_two.name == "${var.project_name}-${var.environment}-part-two-terraform"
    error_message = "IAM policy part-two name format is incorrect for production."
  }

  assert {
    condition     = aws_iam_role_policy_attachment.attach_part_one.role == aws_iam_role.terraform.name
    error_message = "IAM policy part-one is not attached to the role in production."
  }

  assert {
    condition     = aws_iam_role_policy_attachment.attach_part_two.role == aws_iam_role.terraform.name
    error_message = "IAM policy part-two is not attached to the role in production."
  }

  assert {
    condition     = output.terraform_role_arn == aws_iam_role.terraform.arn
    error_message = "The terraform_role_arn output does not match the created role's ARN in production."
  }
}
