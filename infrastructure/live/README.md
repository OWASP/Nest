## Prerequisites

Before the first CI/CD run you must:

1. **IAM role `nest-staging-terraform` (lifecycle)**
   The staging pipeline assumes this role (see the "STSStateManagement" resource below). The role is **created automatically** by the bootstrap when you run it (e.g. the bootstrap workflow that applies `infrastructure/bootstrap` with `staging` in the environments list). On first deployment, the bootstrap run creates `aws_iam_role.terraform` (named `${project}-${env}-terraform`, here `nest-staging-terraform`); subsequent bootstrap runs **update** the existing role. No code or workflow changes are required for this.
   **Manual intervention** may still be needed if you delete the role in AWS, remove it from Terraform state, or need to change the ExternalId (e.g. in the role trust policy or in the staging pipeline configuration).

2. **Create the `nest-staging` IAM user** and attach the inline permissions documented below. This user is used to assume the `nest-staging-terraform` role.

3. **Ensure backend resources exist** and replace the placeholders in the policy and pipeline configuration:
   - **AWS_ACCOUNT_ID** — Your AWS account ID (used in the role ARN).

## Inline Permissions

Use the following inline permissions for the `nest-staging` IAM User.
*Note*: replace the placeholder `AWS_ACCOUNT_ID` with the appropriate value before running the pipeline.

```json
{
    "Version": "2012-10-17",
        "Statement": [
        {
            "Sid": "STSStateManagement",
            "Effect": "Allow",
            "Action": [
                "sts:AssumeRole",
                "sts:TagSession"
            ],
            "Resource": "arn:aws:iam::AWS_ACCOUNT_ID:role/nest-staging-terraform"
        }
    ]
}
```
