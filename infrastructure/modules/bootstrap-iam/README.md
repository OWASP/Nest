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
## Requirements

No requirements.

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_aws"></a> [aws](#provider\_aws) | n/a |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [aws_iam_policy.part_one](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_policy.part_two](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_role.terraform](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy_attachment.attach_part_one](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.attach_part_two](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [aws_iam_policy_document.part_one](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.part_two](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_aws_region"></a> [aws\_region](#input\_aws\_region) | The AWS region to deploy resources in. | `string` | `"us-east-2"` | no |
| <a name="input_aws_role_external_id"></a> [aws\_role\_external\_id](#input\_aws\_role\_external\_id) | The external ID for role assumption. | `string` | n/a | yes |
| <a name="input_environment"></a> [environment](#input\_environment) | The environment name (e.g. staging, production). | `string` | n/a | yes |
| <a name="input_project_name"></a> [project\_name](#input\_project\_name) | The name of the project. | `string` | `"nest"` | no |
| <a name="input_shared_data_bucket_name"></a> [shared\_data\_bucket\_name](#input\_shared\_data\_bucket\_name) | Global S3 bucket for shared public data (e.g. nest.dump) | `string` | `"owasp-nest-shared-data"` | no |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_part_one_policy_arn"></a> [part\_one\_policy\_arn](#output\_part\_one\_policy\_arn) | The ARN of the part one IAM policy. |
| <a name="output_part_two_policy_arn"></a> [part\_two\_policy\_arn](#output\_part\_two\_policy\_arn) | The ARN of the part two IAM policy. |
| <a name="output_terraform_role_arn"></a> [terraform\_role\_arn](#output\_terraform\_role\_arn) | The ARN of the Terraform IAM role. |
<!-- END_TF_DOCS -->
