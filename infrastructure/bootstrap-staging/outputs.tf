output "terraform_role_arn" {
  description = "The ARN of the staging Terraform IAM role."
  value       = module.bootstrap_iam.terraform_role_arn
}
