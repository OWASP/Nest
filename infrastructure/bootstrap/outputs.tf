output "terraform_role_arn" {
  description = "The ARN of the Terraform IAM role."
  value       = aws_iam_role.terraform.arn
}

output "part_one_policy_arn" {
  description = "The ARN of the part one IAM policy."
  value       = aws_iam_policy.part_one.arn
}

output "part_two_policy_arn" {
  description = "The ARN of the part two IAM policy."
  value       = aws_iam_policy.part_two.arn
}
