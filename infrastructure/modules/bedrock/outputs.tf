output "policy_arn" {
  description = "ARN of the policy allowing invocation of the selected Bedrock target."
  value       = aws_iam_policy.main.arn
}
