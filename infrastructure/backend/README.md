## Inline Permissions
Use the following inline permissions for the `nest-backend` IAM User
*Note*: replace ${AWS_ACCOUNT_ID} and ${AWS_BACKEND_KMS_KEY_ARN} with appropriate values.
*Note*: use "*" instead of `AWS_BACKEND_KMS_KEY_ARN` on first `terraform apply`.

```json
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "S3Management",
			"Effect": "Allow",
			"Action": [
				"s3:CreateBucket",
				"s3:DeleteBucket",
				"s3:DeleteBucketPolicy",
				"s3:GetAccelerateConfiguration",
				"s3:GetBucketAcl",
				"s3:GetBucketCors",
				"s3:GetBucketLogging",
				"s3:GetBucketObjectLockConfiguration",
				"s3:GetBucketPolicy",
				"s3:GetBucketPublicAccessBlock",
				"s3:GetBucketRequestPayment",
				"s3:GetBucketTagging",
				"s3:GetBucketVersioning",
				"s3:GetBucketWebsite",
				"s3:GetEncryptionConfiguration",
				"s3:GetLifecycleConfiguration",
				"s3:GetObject",
				"s3:GetReplicationConfiguration",
				"s3:ListBucket",
				"s3:PutBucketLogging",
				"s3:PutBucketObjectLockConfiguration",
				"s3:PutBucketPolicy",
				"s3:PutBucketPublicAccessBlock",
				"s3:PutBucketTagging",
				"s3:PutBucketVersioning",
				"s3:PutEncryptionConfiguration",
				"s3:PutLifecycleConfiguration",
				"s3:PutObject"
			],
			"Resource": [
				"arn:aws:s3:::nest-*-terraform-state*",
				"arn:aws:s3:::nest-*-terraform-state*/*"
			]
		},
		{
			"Sid": "DynamoDBManagement",
			"Effect": "Allow",
			"Action": [
				"dynamodb:CreateTable",
				"dynamodb:DeleteTable",
				"dynamodb:DescribeContinuousBackups",
				"dynamodb:DescribeTable",
				"dynamodb:DescribeTimeToLive",
				"dynamodb:ListTagsOfResource",
				"dynamodb:TagResource",
				"dynamodb:UntagResource",
				"dynamodb:UpdateContinuousBackups",
				"dynamodb:UpdateTable"
			],
			"Resource": "arn:aws:dynamodb:*:${AWS_ACCOUNT_ID}:table/nest-*-terraform-state-lock"
		},
		{
			"Sid": "KMSCreateManagement",
			"Effect": "Allow",
			"Action": [
				"kms:CreateKey",
				"kms:ListAliases",
				"kms:ListKeys"
			],
			"Resource": "*"
		},
		{
			"Sid": "KMSManagement",
			"Effect": "Allow",
			"Action": [
				"kms:CreateAlias",
				"kms:CreateGrant",
				"kms:DeleteAlias",
				"kms:DescribeKey",
				"kms:DisableKeyRotation",
				"kms:EnableKeyRotation",
				"kms:GetKeyPolicy",
				"kms:GetKeyRotationStatus",
				"kms:ListResourceTags",
				"kms:PutKeyPolicy",
				"kms:ScheduleKeyDeletion",
				"kms:TagResource",
				"kms:UntagResource",
				"kms:UpdateAlias",
				"kms:UpdateKeyDescription"
			],
			"Resource": "${AWS_BACKEND_KMS_KEY_ARN}"
		}
	]
}
```
