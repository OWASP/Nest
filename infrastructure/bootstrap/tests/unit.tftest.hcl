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

run "test_staging_resource_names" {
  command = plan

  assert {
    condition = alltrue([
      aws_iam_role.terraform.name == "nest-staging-terraform",
      aws_iam_policy.part_one.name == "nest-staging-part-one-terraform",
      aws_iam_policy.part_two.name == "nest-staging-part-two-terraform",
    ])
    error_message = "Staging bootstrap must only create staging resources."
  }
}

run "test_production_resource_names" {
  command = plan

  variables {
    environment = "production"
  }

  assert {
    condition = alltrue([
      aws_iam_role.terraform.name == "nest-production-terraform",
      aws_iam_policy.part_one.name == "nest-production-part-one-terraform",
      aws_iam_policy.part_two.name == "nest-production-part-two-terraform",
    ])
    error_message = "Production bootstrap must only create production resources."
  }
}

run "test_part_one_policy_size" {
  command = plan

  assert {
    condition     = length(data.aws_iam_policy_document.part_one.minified_json) <= 6144
    error_message = "part_one staging policy exceeds the IAM managed policy size limit of 6144 characters."
  }
}

run "test_part_two_policy_size" {
  command = plan

  assert {
    condition     = length(data.aws_iam_policy_document.part_two.minified_json) <= 6144
    error_message = "part_two staging policy exceeds the IAM managed policy size limit of 6144 characters."
  }
}

run "test_part_one_policy_size_production" {
  command = plan

  variables {
    environment = "production"
  }

  assert {
    condition     = length(data.aws_iam_policy_document.part_one.minified_json) <= 6144
    error_message = "part_one production policy exceeds the IAM managed policy size limit of 6144 characters."
  }
}

run "test_part_two_policy_size_production" {
  command = plan

  variables {
    environment = "production"
  }

  assert {
    condition     = length(data.aws_iam_policy_document.part_two.minified_json) <= 6144
    error_message = "part_two production policy exceeds the IAM managed policy size limit of 6144 characters."
  }
}

run "test_minified_json_is_smaller_than_pretty_json" {
  command = plan

  variables {
    environment = "production"
  }

  assert {
    condition = alltrue([
      length(data.aws_iam_policy_document.part_one.minified_json) < length(data.aws_iam_policy_document.part_one.json),
      length(data.aws_iam_policy_document.part_two.minified_json) < length(data.aws_iam_policy_document.part_two.json),
    ])
    error_message = "IAM policies must use minified_json because pretty JSON exceeds the AWS size limit."
  }
}

run "test_pretty_json_exceeds_limit_for_part_one_production" {
  command = plan

  variables {
    environment = "production"
  }

  assert {
    condition     = length(data.aws_iam_policy_document.part_one.json) > 6144
    error_message = "Expected part_one production pretty JSON to exceed the IAM size limit, proving minified_json is required."
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
        "arn:aws:secretsmanager:${var.aws_region}:160885282306:secret:${var.project_name}-${var.environment}-*",
      ),
      strcontains(
        data.aws_iam_policy_document.part_two.json,
        "arn:aws:secretsmanager:${var.aws_region}:160885282306:secret:/${var.project_name}/${var.environment}/*",
      ),
    ])
    error_message = "The Terraform policy must allow management of the environment Secrets Manager namespace."
  }
}

run "test_environment_scoped_resources_staging" {
  command = plan

  assert {
    condition = alltrue([
      can(regex("${var.project_name}-${var.environment}-", data.aws_iam_policy_document.part_one.json)),
      !can(regex("${var.project_name}-production-", data.aws_iam_policy_document.part_one.json)),
    ])
    error_message = "Policy documents must only reference the configured environment."
  }
}

run "test_staging_policy_names_reference_staging" {
  command = plan

  assert {
    condition = alltrue([
      strcontains(aws_iam_policy.part_one.name, "nest-staging-part-one-terraform"),
      strcontains(aws_iam_policy.part_two.name, "nest-staging-part-two-terraform"),
    ])
    error_message = "Staging policy names must contain staging namespaces."
  }
}

run "test_elb_and_ecs_tagging_staging" {
  command = plan

  assert {
    condition = alltrue([
      !contains(one([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement if statement.Sid == "ELBMgmt"]).Resource, "*"),
      contains(one([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement if statement.Sid == "ELBMgmt"]).Resource, "arn:aws:elasticloadbalancing:${var.aws_region}:160885282306:loadbalancer/app/${var.project_name}-staging-*/*"),
      one([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement if statement.Sid == "ECSTaskDefinitionTagging"]).Resource == "arn:aws:ecs:${var.aws_region}:160885282306:task-definition/${var.project_name}-staging-*:*",
      !contains(one([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement if statement.Sid == "ECSGlobal"]).Action, "ecs:TagResource"),
    ])
    error_message = "ELB management and ECS task-definition tagging must be limited to staging resources."
  }
}

run "test_production_environment_scoped_resources" {
  command = plan

  variables {
    environment = "production"
  }

  assert {
    condition = alltrue([
      can(regex("${var.project_name}-${var.environment}-", data.aws_iam_policy_document.part_one.json)),
      can(regex("TargetTracking-service/${var.project_name}-${var.environment}-", data.aws_iam_policy_document.part_two.json)),
      !can(regex("${var.project_name}-staging-", data.aws_iam_policy_document.part_one.json)),
      !can(regex("${var.project_name}-staging-", data.aws_iam_policy_document.part_two.json)),
      contains(one([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement if statement.Sid == "ELBMgmt"]).Resource, "arn:aws:elasticloadbalancing:${var.aws_region}:160885282306:loadbalancer/app/${var.project_name}-production-*/*"),
      one([for statement in jsondecode(data.aws_iam_policy_document.part_two.json).Statement : statement if statement.Sid == "ECSTaskDefinitionTagging"]).Resource == "arn:aws:ecs:${var.aws_region}:160885282306:task-definition/${var.project_name}-production-*:*",
      strcontains(aws_iam_policy.part_one.name, "nest-production-part-one-terraform"),
      strcontains(aws_iam_policy.part_two.name, "nest-production-part-two-terraform"),
    ])
    error_message = "Production policy documents must only reference production resources."
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
