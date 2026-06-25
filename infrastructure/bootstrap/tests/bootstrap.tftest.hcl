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
  environments         = ["staging", "production"]
  project_name         = "nest"
}

run "test_part_one_policy_size_staging" {
  command = plan

  assert {
    condition     = length(data.aws_iam_policy_document.part_one["staging"].minified_json) <= 6144
    error_message = "part_one staging policy exceeds the IAM managed policy size limit of 6144 characters."
  }
}

run "test_part_one_policy_size_production" {
  command = plan

  assert {
    condition     = length(data.aws_iam_policy_document.part_one["production"].minified_json) <= 6144
    error_message = "part_one production policy exceeds the IAM managed policy size limit of 6144 characters."
  }
}

run "test_part_two_policy_size_staging" {
  command = plan

  assert {
    condition     = length(data.aws_iam_policy_document.part_two["staging"].minified_json) <= 6144
    error_message = "part_two staging policy exceeds the IAM managed policy size limit of 6144 characters."
  }
}

run "test_part_two_policy_size_production" {
  command = plan

  assert {
    condition     = length(data.aws_iam_policy_document.part_two["production"].minified_json) <= 6144
    error_message = "part_two production policy exceeds the IAM managed policy size limit of 6144 characters."
  }
}

run "test_minified_json_is_smaller_than_pretty_json" {
  command = plan

  assert {
    condition = alltrue([
      length(data.aws_iam_policy_document.part_one["production"].minified_json) < length(data.aws_iam_policy_document.part_one["production"].json),
      length(data.aws_iam_policy_document.part_two["production"].minified_json) < length(data.aws_iam_policy_document.part_two["production"].json),
    ])
    error_message = "IAM policies must use minified_json because pretty JSON exceeds the AWS size limit."
  }
}

run "test_pretty_json_exceeds_limit_for_part_one_production" {
  command = plan

  assert {
    condition     = length(data.aws_iam_policy_document.part_one["production"].json) > 6144
    error_message = "Expected part_one production pretty JSON to exceed the IAM size limit, proving minified_json is required."
  }
}

run "test_autoscaling_permissions_in_part_two" {
  command = plan

  assert {
    condition = alltrue([
      can(regex("application-autoscaling:PutScalingPolicy", data.aws_iam_policy_document.part_two["staging"].json)),
      can(regex("cloudwatch:PutMetricAlarm", data.aws_iam_policy_document.part_two["staging"].json)),
      can(regex("iam:CreateServiceLinkedRole", data.aws_iam_policy_document.part_two["staging"].json)),
      can(regex("TargetTracking-service/nest-staging-", data.aws_iam_policy_document.part_two["staging"].json)),
    ])
    error_message = "part_two must include environment-scoped ECS auto-scaling permissions."
  }
}

run "test_autoscaling_permissions_not_in_part_one" {
  command = plan

  assert {
    condition = alltrue([
      can(regex("application-autoscaling:DescribeScalingActivities", data.aws_iam_policy_document.part_one["staging"].json)),
      !can(regex("application-autoscaling:PutScalingPolicy", data.aws_iam_policy_document.part_one["staging"].json)),
      !can(regex("cloudwatch:PutMetricAlarm", data.aws_iam_policy_document.part_one["staging"].json)),
    ])
    error_message = "part_one must include DescribeScalingActivities discovery and exclude ECS auto-scaling management permissions."
  }
}
