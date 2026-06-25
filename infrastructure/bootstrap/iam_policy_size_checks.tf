check "terraform_role_policy_sizes" {
  assert {
    condition = alltrue([
      for environment in var.environments : length(data.aws_iam_policy_document.part_one[environment].minified_json) <= 6144
    ])
    error_message = "part_one exceeds the IAM managed policy size limit of 6144 characters for at least one environment."
  }

  assert {
    condition = alltrue([
      for environment in var.environments : length(data.aws_iam_policy_document.part_two[environment].minified_json) <= 6144
    ])
    error_message = "part_two exceeds the IAM managed policy size limit of 6144 characters for at least one environment."
  }
}
