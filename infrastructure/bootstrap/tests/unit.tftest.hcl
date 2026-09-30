provider "aws" {
  access_key                  = "mock"
  region                      = "us-east-2"
  secret_key                  = "mock"
  skip_credentials_validation = true
  skip_requesting_account_id  = true
}

override_data {
  target = data.aws_caller_identity.current
  values = {
    account_id = "160885282306"
    arn        = "arn:aws:iam::160885282306:user/nest-bootstrap"
    user_id    = "EXAMPLE"
  }
}

variables {
  aws_role_external_id = "test-external-id"
  environment          = "staging"
  project_name         = "nest"
}

run "test_resource_names" {
  command = plan

  assert {
    condition = alltrue([
      aws_iam_role.terraform.name == "${var.project_name}-${var.environment}-terraform",
      aws_iam_policy.part_one.name == "${var.project_name}-${var.environment}-part-one-terraform",
      aws_iam_policy.part_two.name == "${var.project_name}-${var.environment}-part-two-terraform",
      aws_iam_policy.part_three.name == "${var.project_name}-${var.environment}-part-three-terraform",
    ])
    error_message = "Bootstrap resource names must follow the '<project_name>-<environment>-<resource>' format."
  }

  assert {
    condition = alltrue([
      jsondecode(aws_iam_role.terraform.assume_role_policy).Statement[0].Condition.StringEquals["sts:ExternalId"] == var.aws_role_external_id,
      strcontains(jsondecode(aws_iam_role.terraform.assume_role_policy).Statement[0].Principal.AWS, "/${var.project_name}-${var.environment}"),
    ])
    error_message = "IAM role assume role policy must verify the trusted principal is scoped to the environment and the external ID is correct."
  }
}

run "test_part_one_policy_size" {
  command = plan

  assert {
    condition     = length(data.aws_iam_policy_document.part_one.minified_json) <= local.iam_policy_size_limit
    error_message = "part_one policy is ${length(data.aws_iam_policy_document.part_one.minified_json)} characters, exceeding the IAM managed policy size limit of ${local.iam_policy_size_limit} characters."
  }
}

run "test_part_two_policy_size" {
  command = plan

  assert {
    condition     = length(data.aws_iam_policy_document.part_two.minified_json) <= local.iam_policy_size_limit
    error_message = "part_two policy is ${length(data.aws_iam_policy_document.part_two.minified_json)} characters, exceeding the IAM managed policy size limit of ${local.iam_policy_size_limit} characters."
  }
}

run "test_part_three_policy_size" {
  command = plan

  assert {
    condition     = length(data.aws_iam_policy_document.part_three.minified_json) <= local.iam_policy_size_limit
    error_message = "part_three policy is ${length(data.aws_iam_policy_document.part_three.minified_json)} characters, exceeding the IAM managed policy size limit of ${local.iam_policy_size_limit} characters."
  }
}

run "test_secrets_manager_namespace" {
  command = plan

  assert {
    condition = alltrue([
      strcontains(
        data.aws_iam_policy_document.part_three.json,
        "arn:aws:secretsmanager:${var.aws_region}:160885282306:secret:${var.project_name}-${var.environment}-*",
      ),
      strcontains(
        data.aws_iam_policy_document.part_three.json,
        "arn:aws:secretsmanager:${var.aws_region}:160885282306:secret:/${var.project_name}/${var.environment}/*",
      ),
    ])
    error_message = "The Terraform policy must allow management of the Secrets Manager namespace."
  }
}

run "test_minified_json_is_smaller_than_pretty_json" {
  command = plan

  assert {
    condition = alltrue([
      length(data.aws_iam_policy_document.part_one.minified_json) < length(data.aws_iam_policy_document.part_one.json),
      length(data.aws_iam_policy_document.part_two.minified_json) < length(data.aws_iam_policy_document.part_two.json),
      length(data.aws_iam_policy_document.part_three.minified_json) < length(data.aws_iam_policy_document.part_three.json),
    ])
    error_message = "IAM policies must use minified_json because pretty JSON exceeds the AWS size limit."
  }
}

run "test_pretty_json_exceeds_limit_for_part_one" {
  command = plan

  assert {
    condition     = length(data.aws_iam_policy_document.part_one.json) > local.iam_policy_size_limit
    error_message = "Expected part_one pretty JSON to exceed the IAM size limit for the configured environment, proving minified_json is required."
  }
}

run "test_autoscaling_permissions_in_part_two" {
  command = plan

  assert {
    condition = alltrue([
      strcontains(data.aws_iam_policy_document.part_two.json, "application-autoscaling:PutScalingPolicy"),
      strcontains(data.aws_iam_policy_document.part_two.json, "cloudwatch:PutMetricAlarm"),
      strcontains(data.aws_iam_policy_document.part_two.json, "iam:CreateServiceLinkedRole"),
      strcontains(data.aws_iam_policy_document.part_two.json, "TargetTracking-service/${var.project_name}-${var.environment}-"),
    ])
    error_message = "part_two must include environment-scoped ECS auto-scaling permissions."
  }
}

run "test_autoscaling_permissions_not_in_part_one" {
  command = plan

  assert {
    condition = alltrue([
      strcontains(data.aws_iam_policy_document.part_one.json, "application-autoscaling:DescribeScalingActivities"),
      !strcontains(data.aws_iam_policy_document.part_one.json, "application-autoscaling:PutScalingPolicy"),
      !strcontains(data.aws_iam_policy_document.part_one.json, "cloudwatch:PutMetricAlarm"),
    ])
    error_message = "part_one must include DescribeScalingActivities discovery and exclude ECS auto-scaling management permissions."
  }
}

run "test_shared_bucket_permissions_non_production" {
  command = plan

  assert {
    condition = alltrue([
      contains(one([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement if statement.Sid == "S3Management"]).Resource, "arn:aws:s3:::${var.shared_data_bucket_name}"),
      contains(one([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement if statement.Sid == "S3Management"]).Resource, "arn:aws:s3:::${var.shared_data_bucket_name}/*"),
      !contains(one([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement if statement.Sid == "S3WriteManagement"]).Resource, "arn:aws:s3:::${var.shared_data_bucket_name}"),
      !contains(one([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement if statement.Sid == "S3WriteManagement"]).Resource, "arn:aws:s3:::${var.shared_data_bucket_name}/*"),
      !contains([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement.Sid], "S3SharedBucketRestricted"),
    ])
    error_message = "Non-production environments must have read access to the shared data bucket but no write access."
  }
}

run "test_shared_bucket_permissions_production" {
  command = plan

  variables {
    environment = "production"
  }

  assert {
    condition = alltrue([
      contains(one([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement if statement.Sid == "S3Management"]).Resource, "arn:aws:s3:::${var.shared_data_bucket_name}"),
      contains(one([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement if statement.Sid == "S3Management"]).Resource, "arn:aws:s3:::${var.shared_data_bucket_name}/*"),
      contains(one([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement if statement.Sid == "S3WriteManagement"]).Resource, "arn:aws:s3:::${var.shared_data_bucket_name}"),
      contains(one([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement if statement.Sid == "S3WriteManagement"]).Resource, "arn:aws:s3:::${var.shared_data_bucket_name}/*"),
      !contains([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement.Sid], "S3SharedBucketRestricted"),
    ])
    error_message = "The environment with management privileges must have full read and write access to the shared data bucket via S3Management and S3WriteManagement."
  }
}
