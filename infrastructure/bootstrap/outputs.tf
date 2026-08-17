output "terraform_role_arn" {
  description = "The ARN of the Terraform IAM role."
  value       = aws_iam_role.terraform.arn
}
