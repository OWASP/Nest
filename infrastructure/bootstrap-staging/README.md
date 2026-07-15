# Bootstrap — Staging

Per-environment Terraform root for the **staging** bootstrap IAM resources.

This root manages only `nest-staging-terraform` IAM role and its policies,
using the shared `bootstrap-iam` module. It has its own Terraform state file
(`staging/bootstrap/terraform.tfstate`), ensuring staging deploys cannot
modify production IAM resources.

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
|-----|-------|
| Backend | S3 |
| State key | `staging/bootstrap/terraform.tfstate` |

## Related

- [Shared module](../modules/bootstrap-iam/README.md)
- [Production bootstrap](../bootstrap-production/README.md)
- [Original bootstrap (deprecated)](../bootstrap/README.md)
