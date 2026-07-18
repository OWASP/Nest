# Bootstrap IAM Infrastructure

This is the single Terraform root directory used to bootstrap the IAM resources for the OWASP Nest project. It configures the IAM roles and policies that allow Terraform and CI/CD pipelines to manage AWS resources for staging and production environments.

## Multi-Environment Single-Root Design

Unlike normal environment infrastructure directories, this single root is shared to deploy both `staging` and `production` resources. The specific target environment is injected via the `environment` Terraform variable.

### Alignment of Environment and State Key

It is critical that you match the `environment` variable with the correct S3 backend `key` in the state bucket.

- **Staging**:
  - `environment = "staging"`
  - state key: `staging/bootstrap/terraform.tfstate`
- **Production**:
  - `environment = "production"`
  - state key: `production/bootstrap/terraform.tfstate`

> [!WARNING]
> Terraform itself cannot prevent an operator from pairing the wrong environment variable with the wrong state key (e.g., setting `environment = "staging"` while using the `production` state file). You must ensure these two inputs are kept aligned.

---

## Local Usage Instructions

To run plans or apply changes locally:

1. Copy the example variable and backend configuration files:

   ```bash
   cp terraform.tfbackend.example terraform.tfbackend
   cp terraform.tfvars.example terraform.tfvars
   ```

2. Edit `terraform.tfbackend`:
   - Replace `REPLACE_WITH_TF_STATE_BUCKET_NAME` with your actual bootstrap state bucket name.
   - Align the `key` parameter to target the desired environment (`staging/bootstrap/terraform.tfstate` or `production/bootstrap/terraform.tfstate`).

3. Edit `terraform.tfvars`:
   - Set `environment` to matching environment (`staging` or `production`).
   - Set `aws_role_external_id` to the external ID used for role assumption.

4. Initialize the Terraform backend:

   Using `-reconfigure` is required to safely switch between environment keys without migrating the previous environment's state:

   ```bash
   terraform init -reconfigure -backend-config=terraform.tfbackend
   ```

> [!IMPORTANT]
> **State Migration Prerequisite**: If applying this refactored configuration to an existing environment, you **must not** run `terraform plan` or `terraform apply` before migrating the legacy shared state. Running them before migrating will make Terraform attempt to recreate already-existing roles and policies, causing name conflicts and rollout failures.
>
> Please follow the [State Migration Instructions](#state-migration-one-time-post-merge) below to split the legacy state first.

5. Run Plan or Apply:

   ```bash
   terraform plan
   terraform apply
   ```

---

## Inline Permissions

Ensure your `nest-bootstrap` IAM User has the following inline permissions attached before running bootstrap operations. Replace the placeholders with appropriate values.

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
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 6.53.0 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_aws"></a> [aws](#provider\_aws) | 6.53.0 |

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
| <a name="input_environment"></a> [environment](#input\_environment) | The environment name (staging or production). | `string` | n/a | yes |
| <a name="input_project_name"></a> [project\_name](#input\_project\_name) | The name of the project. | `string` | `"nest"` | no |
| <a name="input_shared_data_bucket_name"></a> [shared\_data\_bucket\_name](#input\_shared\_data\_bucket\_name) | Global S3 bucket for shared public data (e.g. nest.dump) | `string` | `"owasp-nest-shared-data"` | no |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_part_one_policy_arn"></a> [part\_one\_policy\_arn](#output\_part\_one\_policy\_arn) | The ARN of the part one IAM policy. |
| <a name="output_part_two_policy_arn"></a> [part\_two\_policy\_arn](#output\_part\_two\_policy\_arn) | The ARN of the part two IAM policy. |
| <a name="output_terraform_role_arn"></a> [terraform\_role\_arn](#output\_terraform\_role\_arn) | The ARN of the Terraform IAM role. |
<!-- END_TF_DOCS -->

---

## State Migration (One-Time, Post-Merge)

Existing shared bootstrap state requires maintainer-led migration to split the old shared state into staging and production state files. The resources must be renamed from their old map keys (e.g. `aws_iam_role.terraform["staging"]` / `aws_iam_role.terraform["production"]`) to their direct single-root equivalents (e.g. `aws_iam_role.terraform`) before the new root is used against AWS.

### Step 1. Back up the old shared state
Initialize the backend for the old shared state and pull a backup:
```bash
terraform -chdir=infrastructure/bootstrap init -reconfigure \
  -backend-config="bucket=<REAL_BUCKET>" \
  -backend-config="region=us-east-2" \
  -backend-config="key=<OLD_SHARED_KEY>"

terraform -chdir=infrastructure/bootstrap state pull > shared_bootstrap_backup.tfstate
```

### Step 2. Migrate Staging State
Extract and rename the staging resources into the new staging state file:
1. Create a copy of the backup:
   ```bash
   cp shared_bootstrap_backup.tfstate staging_bootstrap.tfstate
   ```
2. Rename the staging resources to their direct, non-loop addresses inside the state copy:
   ```bash
   terraform state mv -state=staging_bootstrap.tfstate 'aws_iam_role.terraform["staging"]' aws_iam_role.terraform
   terraform state mv -state=staging_bootstrap.tfstate 'aws_iam_policy.part_one["staging"]' aws_iam_policy.part_one
   terraform state mv -state=staging_bootstrap.tfstate 'aws_iam_policy.part_two["staging"]' aws_iam_policy.part_two
   terraform state mv -state=staging_bootstrap.tfstate 'aws_iam_role_policy_attachment.attach_part_one["staging"]' aws_iam_role_policy_attachment.attach_part_one
   terraform state mv -state=staging_bootstrap.tfstate 'aws_iam_role_policy_attachment.attach_part_two["staging"]' aws_iam_role_policy_attachment.attach_part_two
   ```
3. Remove the untracked production resources from the staging state file:
   ```bash
   terraform state rm -state=staging_bootstrap.tfstate 'aws_iam_role.terraform["production"]'
   terraform state rm -state=staging_bootstrap.tfstate 'aws_iam_policy.part_one["production"]'
   terraform state rm -state=staging_bootstrap.tfstate 'aws_iam_policy.part_two["production"]'
   terraform state rm -state=staging_bootstrap.tfstate 'aws_iam_role_policy_attachment.attach_part_one["production"]'
   terraform state rm -state=staging_bootstrap.tfstate 'aws_iam_role_policy_attachment.attach_part_two["production"]'
   ```
4. Push the staging state to its new per-environment S3 location:
   ```bash
   terraform -chdir=infrastructure/bootstrap init -reconfigure \
     -backend-config="bucket=<REAL_BUCKET>" \
     -backend-config="region=us-east-2" \
     -backend-config="key=staging/bootstrap/terraform.tfstate"
   
   terraform -chdir=infrastructure/bootstrap state push staging_bootstrap.tfstate
   ```

### Step 3. Migrate Production State
Extract and rename the production resources into the new production state file:
1. Create a copy of the backup:
   ```bash
   cp shared_bootstrap_backup.tfstate production_bootstrap.tfstate
   ```
2. Rename the production resources to their direct, non-loop addresses inside the state copy:
   ```bash
   terraform state mv -state=production_bootstrap.tfstate 'aws_iam_role.terraform["production"]' aws_iam_role.terraform
   terraform state mv -state=production_bootstrap.tfstate 'aws_iam_policy.part_one["production"]' aws_iam_policy.part_one
   terraform state mv -state=production_bootstrap.tfstate 'aws_iam_policy.part_two["production"]' aws_iam_policy.part_two
   terraform state mv -state=production_bootstrap.tfstate 'aws_iam_role_policy_attachment.attach_part_one["production"]' aws_iam_role_policy_attachment.attach_part_one
   terraform state mv -state=production_bootstrap.tfstate 'aws_iam_role_policy_attachment.attach_part_two["production"]' aws_iam_role_policy_attachment.attach_part_two
   ```
3. Remove the untracked staging resources from the production state file:
   ```bash
   terraform state rm -state=production_bootstrap.tfstate 'aws_iam_role.terraform["staging"]'
   terraform state rm -state=production_bootstrap.tfstate 'aws_iam_policy.part_one["staging"]'
   terraform state rm -state=production_bootstrap.tfstate 'aws_iam_policy.part_two["staging"]'
   terraform state rm -state=production_bootstrap.tfstate 'aws_iam_role_policy_attachment.attach_part_one["staging"]'
   terraform state rm -state=production_bootstrap.tfstate 'aws_iam_role_policy_attachment.attach_part_two["staging"]'
   ```
4. Push the production state to its new per-environment S3 location:
   ```bash
   terraform -chdir=infrastructure/bootstrap init -reconfigure \
     -backend-config="bucket=<REAL_BUCKET>" \
     -backend-config="region=us-east-2" \
     -backend-config="key=production/bootstrap/terraform.tfstate"
   
   terraform -chdir=infrastructure/bootstrap state push production_bootstrap.tfstate
   ```

### Step 4. Verify Both Migrations
Run a plan on each environment config to verify no resources are changed or destroyed:
- Run plan for staging:
  ```bash
  terraform -chdir=infrastructure/bootstrap init -reconfigure \
    -backend-config="bucket=<REAL_BUCKET>" \
    -backend-config="region=us-east-2" \
    -backend-config="key=staging/bootstrap/terraform.tfstate"
  
  terraform -chdir=infrastructure/bootstrap plan -var="environment=staging"
  ```
- Run plan for production:
  ```bash
  terraform -chdir=infrastructure/bootstrap init -reconfigure \
    -backend-config="bucket=<REAL_BUCKET>" \
    -backend-config="region=us-east-2" \
    -backend-config="key=production/bootstrap/terraform.tfstate"
  
  terraform -chdir=infrastructure/bootstrap plan -var="environment=production"
  ```
Both plans must return `No changes. Your infrastructure matches the configuration.`, indicating the migration was 100% successful and clean.
