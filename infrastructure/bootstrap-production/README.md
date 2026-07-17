# Bootstrap — Production

Per-environment Terraform root for the **production** bootstrap IAM resources.

This root manages only `nest-production-terraform` IAM role and its policies,
using the shared `bootstrap-iam` module. It has its own Terraform state file
(`production/bootstrap/terraform.tfstate`), preventing Terraform state collisions
with the staging root. IAM access isolation (ensuring the production role cannot
modify staging resources) is enforced by the environment-scoped policies defined
in the shared `bootstrap-iam` module.

## Setup

Before initializing, copy and configure the example files:

```bash
# 1. Configure backend (set the S3 bucket name)
cp terraform.tfbackend.example terraform.tfbackend
# Edit terraform.tfbackend and replace REPLACE_WITH_TF_STATE_BUCKET_NAME

# 2. Configure variables (set aws_role_external_id)
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars and replace AWS_ROLE_EXTERNAL_ID
```

## Usage

```bash
# Initialize
terraform init -backend-config=terraform.tfbackend

# Plan
terraform plan

# Apply
terraform apply
```

## State

| Key | Value |
| --- | --- |
| Backend | S3 |
| State key | `production/bootstrap/terraform.tfstate` |

## Related

- [Shared module](../modules/bootstrap-iam/README.md)
- [Staging bootstrap](../bootstrap-staging/README.md)
- [Original bootstrap (deprecated)](../bootstrap/README.md)

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | ~> 1.14.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 6.53.0 |

## Providers

No providers.

## Modules

| Name | Source | Version |
| ---- | ------ | ------- |
| <a name="module_bootstrap_iam"></a> [bootstrap\_iam](#module\_bootstrap\_iam) | ../modules/bootstrap-iam | n/a |

## Resources

No resources.

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_aws_region"></a> [aws\_region](#input\_aws\_region) | The AWS region to deploy resources in. | `string` | `"us-east-2"` | no |
| <a name="input_aws_role_external_id"></a> [aws\_role\_external\_id](#input\_aws\_role\_external\_id) | The external ID for role assumption. | `string` | n/a | yes |
| <a name="input_project_name"></a> [project\_name](#input\_project\_name) | The name of the project. | `string` | `"nest"` | no |
| <a name="input_shared_data_bucket_name"></a> [shared\_data\_bucket\_name](#input\_shared\_data\_bucket\_name) | Global S3 bucket for shared public data (e.g. nest.dump) | `string` | `"owasp-nest-shared-data"` | no |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_terraform_role_arn"></a> [terraform\_role\_arn](#output\_terraform\_role\_arn) | The ARN of the production Terraform IAM role. |
<!-- END_TF_DOCS -->
