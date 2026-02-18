## Inline Permissions
Use the following inline permissions for the `nest-staging` IAM User
*Note*: replace ${...} with appropriate values.

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
			"Resource": "arn:aws:dynamodb:ap-south-1:${AWS_ACCOUNT_ID}:table/nest-staging-terraform-state-lock"
		},
        {
            "Sid": "KMSStateManagement",
            "Effect": "Allow",
            "Action": [
                "kms:Decrypt"
            ],
            "Resource": "${AWS_BACKEND_KMS_KEY_ARN}"
        },
        {
            "Sid": "STSStateManagement",
            "Effect": "Allow",
            "Action": [
                "sts:AssumeRole",
                "sts:TagSession"
            ],
            "Resource": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/nest-staging-terraform"
        }
    ]
}
```
