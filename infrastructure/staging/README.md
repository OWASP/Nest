## Prerequisites

Before the first CI/CD run you must:

1. **IAM role `nest-staging-terraform` (lifecycle)**
   The staging pipeline assumes this role (see the "STSStateManagement" resource below). The role is **created automatically** by the bootstrap when you run it (e.g. the bootstrap workflow that applies `infrastructure/bootstrap` with `staging` in the environments list). On first deployment, the bootstrap run creates `aws_iam_role.terraform` (named `${project}-${env}-terraform`, here `nest-staging-terraform`); subsequent bootstrap runs **update** the existing role. No code or workflow changes are required for this.
   **Manual intervention** may still be needed if you delete the role in AWS, remove it from Terraform state, or need to change the ExternalId (e.g. in the role trust policy or in the staging pipeline configuration).

2. **Create the `nest-staging` IAM user** and attach the inline permissions documented below. This user is used to assume the `nest-staging-terraform` role and to access the Terraform backend (S3 state bucket, DynamoDB state lock table, KMS key).

3. **Ensure backend resources exist** and replace the placeholders in the policy and pipeline configuration:
   - **AWS_ACCOUNT_ID** — Your AWS account ID (used in the role ARN and DynamoDB resource).
   - **AWS_REGION** — The region where the state DynamoDB table and (if applicable) KMS key live.
   - **AWS_BACKEND_KMS_KEY_ARN** — The ARN of the KMS key used to encrypt the Terraform state bucket.

   The S3 state bucket name pattern (`nest-staging-terraform-state-*`), DynamoDB table name (`nest-staging-terraform-state-lock`), and the role name must match what is provisioned (e.g. by the state and bootstrap steps). Replace all placeholders before running the pipeline.

## Inline Permissions

Use the following inline permissions for the `nest-staging` IAM User.
*Note*: replace the placeholders (`AWS_ACCOUNT_ID`, `AWS_REGION`, `AWS_BACKEND_KMS_KEY_ARN`) with appropriate values before running the pipeline.

```json
{
    "Version": "2012-10-17",
        "Statement": [
  {
   "Sid": "S3StateManagement",
   "Effect": "Allow",
   "Action": [
    "s3:GetObject",
    "s3:PutObject",
    "s3:ListBucket"
   ],
   "Resource": [
    "arn:aws:s3:::nest-staging-terraform-state-*",
    "arn:aws:s3:::nest-staging-terraform-state-*/*"
   ]
  },
  {
   "Sid": "DynamoDBStateManagement",
   "Effect": "Allow",
   "Action": [
    "dynamodb:GetItem",
    "dynamodb:PutItem",
    "dynamodb:DeleteItem"
   ],
   "Resource": "arn:aws:dynamodb:AWS_REGION:AWS_ACCOUNT_ID:table/nest-staging-terraform-state-lock"
  },
        {
            "Sid": "KMSStateManagement",
            "Effect": "Allow",
            "Action": [
                "kms:Decrypt"
            ],
            "Resource": "AWS_BACKEND_KMS_KEY_ARN"
        },
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
