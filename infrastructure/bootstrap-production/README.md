# Bootstrap — Production

Per-environment Terraform root for the **production** bootstrap IAM resources.

This root manages only `nest-production-terraform` IAM role and its policies,
using the shared `bootstrap-iam` module. It has its own Terraform state file
(`production/bootstrap/terraform.tfstate`), ensuring production deploys cannot
modify staging IAM resources.

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
| State key | `production/bootstrap/terraform.tfstate` |

## Related

- [Shared module](../modules/bootstrap-iam/README.md)
- [Staging bootstrap](../bootstrap-staging/README.md)
- [Original bootstrap (deprecated)](../bootstrap/README.md)
