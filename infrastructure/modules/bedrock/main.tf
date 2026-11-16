terraform {
  required_version = "~> 1.16.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.67.0"
    }
  }
}

data "aws_bedrock_foundation_model" "main" {
  count    = var.target_type == "foundation-model" ? 1 : 0
  model_id = var.model_name
}

data "aws_bedrock_inference_profile" "main" {
  count                = var.target_type == "inference-profile" ? 1 : 0
  inference_profile_id = var.model_name
}

resource "aws_iam_policy" "main" {
  name        = "${var.name_prefix}-bedrock"
  description = "Allow NestBot to invoke the selected Bedrock target."
  tags        = var.common_tags

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat(
      [for model in data.aws_bedrock_foundation_model.main : {
        Effect   = "Allow"
        Action   = ["bedrock:InvokeModel"]
        Resource = [model.model_arn]
      }],
      flatten([for profile in data.aws_bedrock_inference_profile.main : [
        {
          Effect   = "Allow"
          Action   = ["bedrock:InvokeModel", "bedrock:GetInferenceProfile"]
          Resource = [profile.inference_profile_arn]
        },
        {
          Effect   = "Allow"
          Action   = ["bedrock:InvokeModel"]
          Resource = [for model in profile.models : model.model_arn]
          Condition = {
            StringEquals = {
              "bedrock:InferenceProfileArn" = profile.inference_profile_arn
            }
          }
        }
      ]])
    )
  })
}
