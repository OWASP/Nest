## Users
`bootstrap` creates a role for each environment that IAM users can assume.
These users are listed in the `var.environments` variable.
Ensure your IAM Users follow the naming convention:
- nest-${var.environment}

Example: `nest-staging`, `nest-bootstrap`, etc.

## Inline Permissions
Use the following inline permissions for the `nest-bootstrap` IAM User
*Note*: replace ${AWS_ACCOUNT_ID} and ${AWS_BACKEND_KMS_KEY_ARN} with appropriate values.

```json
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "S3StateAccess",
			"Effect": "Allow",
			"Action": [
				"s3:GetObject",
				"s3:ListBucket",
				"s3:PutObject"
			],
			"Resource": [
				"arn:aws:s3:::nest-terraform-state-bootstrap-*",
				"arn:aws:s3:::nest-terraform-state-bootstrap-*/*"
			]
		},
		{
			"Sid": "DynamoDBStateLocking",
			"Effect": "Allow",
			"Action": [
				"dynamodb:DeleteItem",
				"dynamodb:DescribeTable",
				"dynamodb:GetItem",
				"dynamodb:PutItem"
			],
			"Resource": "arn:aws:dynamodb:*:${AWS_ACCOUNT_ID}:table/nest-terraform-state-lock-bootstrap"
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
				"arn:aws:iam::${AWS_ACCOUNT_ID}:role/nest-*-terraform",
				"arn:aws:iam::${AWS_ACCOUNT_ID}:policy/nest-*-terraform"
			]
		},
		{
			"Sid": "KMSManagement",
			"Effect": "Allow",
			"Action": [
				"kms:Decrypt"
			],
			"Resource": "${AWS_BACKEND_KMS_KEY_ARN}"
		}
	]
}
```
