## Users

`bootstrap` creates a role for each environment that IAM users can assume.
These users are listed in the `var.environments` variable.
Ensure your IAM Users follow the naming convention:

- nest-${var.environment}

Example: `nest-staging`, `nest-bootstrap`, etc.

## Inline Permissions

Use the following inline permissions for the `nest-bootstrap` IAM User
*Note*: replace the placeholders with appropriate values.

```json
{
 "Version": "2012-10-17",
 "Statement": [
  {
   "Sid": "S3StateAccess",
   "Effect": "Allow",
   "Action": [
    "s3:DeleteObject",
    "s3:GetObject",
    "s3:ListBucket",
    "s3:PutObject"
   ],
   "Resource": [
    "arn:aws:s3:::nest-bootstrap-terraform-state-*",
    "arn:aws:s3:::nest-bootstrap-terraform-state-*/*"
   ]
  },
  {
   "Sid": "IAMManagement",
   "Effect": "Allow",
   "Action": [
    "iam:AttachRolePolicy",
    "iam:CreatePolicy",
    "iam:CreatePolicyVersion",
    "iam:CreateRole",
    "iam:DeletePolicy",
    "iam:DeletePolicyVersion",
    "iam:DeleteRole",
    "iam:DeleteRolePolicy",
    "iam:DetachRolePolicy",
    "iam:GetPolicy",
    "iam:GetPolicyVersion",
    "iam:GetRole",
    "iam:GetRolePolicy",
    "iam:ListAttachedRolePolicies",
    "iam:ListInstanceProfilesForRole",
    "iam:ListPolicyVersions",
    "iam:ListRolePolicies",
    "iam:PutRolePolicy",
    "iam:TagPolicy",
    "iam:TagRole",
    "iam:UntagPolicy",
    "iam:UntagRole",
    "iam:UpdateAssumeRolePolicy",
    "iam:UpdateRole"
   ],
   "Resource": [
    "arn:aws:iam::AWS_ACCOUNT_ID:role/nest-*-terraform",
    "arn:aws:iam::AWS_ACCOUNT_ID:policy/nest-*-terraform"
   ]
  },
  {
   "Sid": "KMSManagement",
   "Effect": "Allow",
   "Action": [
    "kms:Decrypt"
   ],
   "Resource": "AWS_BACKEND_KMS_KEY_ARN"
  }
 ]
}
```

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | ~> 1.14.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 6.36.0 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_aws"></a> [aws](#provider\_aws) | 6.36.0 |

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
| <a name="input_environments"></a> [environments](#input\_environments) | The environments to create Terraform roles for. | `list(string)` | <pre>[<br/>  "staging",<br/>  "production"<br/>]</pre> | no |
| <a name="input_project_name"></a> [project\_name](#input\_project\_name) | The name of the project. | `string` | `"nest"` | no |
| <a name="input_shared_data_bucket_name"></a> [shared\_data\_bucket\_name](#input\_shared\_data\_bucket\_name) | Global S3 bucket for shared public data (e.g. nest.dump) | `string` | `"owasp-nest-shared-data"` | no |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_terraform_role_arns"></a> [terraform\_role\_arns](#output\_terraform\_role\_arns) | The ARNs of the Terraform IAM roles, keyed by environment. |
<!-- END_TF_DOCS -->
