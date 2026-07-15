# Bootstrap IAM Module

Reusable Terraform module that creates environment-scoped IAM resources for CI/CD
bootstrap. Each invocation manages a **single** environment (staging or production),
eliminating cross-environment blast radius.

## Usage

```hcl
module "bootstrap_iam" {
  source = "../modules/bootstrap-iam"

  environment          = "staging"
  aws_region           = "us-east-2"
  aws_role_external_id = var.aws_role_external_id
  project_name         = "nest"
}
```

## Resources Created

- `aws_iam_role.terraform` — Terraform execution role with ExternalId trust policy
- `aws_iam_policy.part_one` — IAM policy (discovery, ACM, logs, EC2, ECR, ECS, RDS, etc.)
- `aws_iam_policy.part_two` — IAM policy (autoscaling, ELB, EventBridge, IAM, KMS, S3, Secrets Manager, SSM)
- `aws_iam_role_policy_attachment.attach_part_one` — Attaches part one to the role
- `aws_iam_role_policy_attachment.attach_part_two` — Attaches part two to the role

<!-- BEGIN_TF_DOCS -->
<!-- END_TF_DOCS -->
