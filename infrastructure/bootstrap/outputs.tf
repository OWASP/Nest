output "terraform_role_arns" {
  description = "The ARNs of the Terraform IAM roles, keyed by environment."
  value       = { for env in local.environments : env => aws_iam_role.terraform[env].arn }
}
