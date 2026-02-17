# Policies

- Minimum policies required to use the terraform remote backend:
(Replace ${} variables appropriately)

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
				"arn:aws:s3:::${TERRAFORM_STATE_BUCKET_NAME}",
				"arn:aws:s3:::${TERRAFORM_STATE_BUCKET_NAME}/*"
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
            "Resource": "arn:aws:dynamodb:${AWS_REGION}:${AWS_ACCOUNT_ID}:table/${TERRAFORM_DYNAMODB_TABLE_NAME}"
        },
        {
            "Sid": "KMSStateManagement",
            "Effect": "Allow",
            "Action": [
                "kms:Decrypt"
            ],
            "Resource": "${AWS_BACKEND_KMS_KEY}"
        }
    ]
}
```
