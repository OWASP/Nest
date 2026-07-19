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
    ])
    error_message = "Bootstrap resource names must follow the '<project_name>-<environment>-<resource>' format."
  }
}

run "test_part_one_policy_size" {
  command = plan

  assert {
    condition     = length(data.aws_iam_policy_document.part_one.minified_json) <= local.iam_policy_size_limit
    error_message = "part_one policy exceeds the IAM managed policy size limit of ${local.iam_policy_size_limit} characters."
  }
}

run "test_part_two_policy_size" {
  command = plan

  assert {
    condition     = length(data.aws_iam_policy_document.part_two.minified_json) <= local.iam_policy_size_limit
    error_message = "part_two policy exceeds the IAM managed policy size limit of ${local.iam_policy_size_limit} characters."
  }
}

run "test_minified_json_is_smaller_than_pretty_json" {
  command = plan

  assert {
    condition = alltrue([
      length(data.aws_iam_policy_document.part_one.minified_json) < length(data.aws_iam_policy_document.part_one.json),
      length(data.aws_iam_policy_document.part_two.minified_json) < length(data.aws_iam_policy_document.part_two.json),
    ])
    error_message = "IAM policies must use minified_json because pretty JSON exceeds the AWS size limit."
  }
}

run "test_pretty_json_exceeds_limit_for_part_one" {
  command = plan

  variables {
    environment = "production"
  }

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

run "test_secrets_manager_namespace" {
  command = plan

  assert {
    condition = alltrue([
      strcontains(
        data.aws_iam_policy_document.part_two.json,
        "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:${var.project_name}-${var.environment}-*",
      ),
      strcontains(
        data.aws_iam_policy_document.part_two.json,
        "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:/${var.project_name}/${var.environment}/*",
      ),
    ])
    error_message = "The Terraform policy must allow management of the environment Secrets Manager namespace."
  }
}

run "test_environment_scoped_resources" {
  command = plan

  assert {
    condition = alltrue([
      can(regex("${var.project_name}-${var.environment}-", data.aws_iam_policy_document.part_one.json)),
      !can(regex("${var.project_name}-${var.environment == "staging" ? "production" : "staging"}-", data.aws_iam_policy_document.part_one.json)),
    ])
    error_message = "Policy documents must only reference the configured environment."
  }
}

run "test_elb_and_ecs_tagging" {
  command = plan

  assert {
    condition = alltrue([
      !contains(one([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement if statement.Sid == "ELBMgmt"]).Resource, "*"),
      contains(one([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement if statement.Sid == "ELBMgmt"]).Resource, "arn:aws:elasticloadbalancing:${var.aws_region}:${data.aws_caller_identity.current.account_id}:loadbalancer/app/${var.project_name}-${var.environment}-*/*"),
      one([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement if statement.Sid == "ECSTaskDefinitionTagging"]).Resource == "arn:aws:ecs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:task-definition/${var.project_name}-${var.environment}-*:*",
      !contains(one([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement if statement.Sid == "ECSGlobal"]).Action, "ecs:TagResource"),
    ])
    error_message = "ELB management and ECS task-definition tagging must be limited to the active environment resources."
  }
}

run "test_environment_scoped_resources_with_env_override" {
  command = plan

  variables {
    environment = "production"
  }

  assert {
    condition = alltrue([
      can(regex("${var.project_name}-${var.environment}-", data.aws_iam_policy_document.part_one.json)),
      can(regex("TargetTracking-service/${var.project_name}-${var.environment}-", data.aws_iam_policy_document.part_two.json)),
      !can(regex("${var.project_name}-${var.environment == "production" ? "staging" : "production"}-", data.aws_iam_policy_document.part_one.json)),
      !can(regex("${var.project_name}-${var.environment == "production" ? "staging" : "production"}-", data.aws_iam_policy_document.part_two.json)),
      contains(one([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement if statement.Sid == "ELBMgmt"]).Resource, "arn:aws:elasticloadbalancing:${var.aws_region}:${data.aws_caller_identity.current.account_id}:loadbalancer/app/${var.project_name}-${var.environment}-*/*"),
      one([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement if statement.Sid == "ECSTaskDefinitionTagging"]).Resource == "arn:aws:ecs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:task-definition/${var.project_name}-${var.environment}-*:*",
      strcontains(aws_iam_policy.part_one.name, "${var.project_name}-${var.environment}-part-one-terraform"),
      strcontains(aws_iam_policy.part_two.name, "${var.project_name}-${var.environment}-part-two-terraform"),
    ])
    error_message = "Policy documents must only reference the active environment resources."
  }
}

run "test_invalid_environment_rejected" {
  command = plan

  variables {
    environment = "development"
  }

  expect_failures = [
    var.environment
  ]
}

run "test_shared_bucket_permissions" {
  command = plan

  assert {
    condition = alltrue([
      contains([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement.Sid], "S3SharedBucketRestricted"),
      !contains(one([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement if statement.Sid == "S3SharedBucketRestricted"]).Action, "s3:PutObject"),
      contains(one([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement if statement.Sid == "S3SharedBucketRestricted"]).Action, "s3:Get*"),
    ])
    error_message = "Staging/non-production environments must have read-only access to the shared data bucket (no PutObject permission)."
  }
}

run "test_shared_bucket_permissions_with_env_override" {
  command = plan

  variables {
    environment = "production"
  }

  assert {
    condition = alltrue([
      !contains([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement.Sid], "S3SharedBucketRestricted"),
      contains(one([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement if statement.Sid == "S3Mgmt"]).Resource, "arn:aws:s3:::owasp-nest-shared-data/*"),
    ])
    error_message = "The environment with management privileges must manage the shared data bucket via S3Mgmt and not use S3SharedBucketRestricted."
  }
}
