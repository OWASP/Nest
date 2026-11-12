locals {
  nestbot_bedrock_enabled = local.nestbot_enabled && var.nestbot_llm_provider == "bedrock"
}

data "aws_bedrock_foundation_model" "nestbot" {
  count    = local.nestbot_bedrock_enabled && var.nestbot_bedrock_target_type == "foundation-model" ? 1 : 0
  model_id = var.nestbot_bedrock_model_name
}

data "aws_bedrock_inference_profile" "nestbot" {
  count                = local.nestbot_bedrock_enabled && var.nestbot_bedrock_target_type == "inference-profile" ? 1 : 0
  inference_profile_id = var.nestbot_bedrock_model_name
}

resource "aws_iam_policy" "nestbot_bedrock" {
  count       = local.nestbot_bedrock_enabled ? 1 : 0
  name        = "${var.project_name}-${var.environment}-nestbot-bedrock"
  description = "Allow NestBot to invoke the selected Bedrock target."
  tags        = local.common_tags

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat(
      [for model in data.aws_bedrock_foundation_model.nestbot : {
        Effect   = "Allow"
        Action   = ["bedrock:InvokeModel"]
        Resource = [model.model_arn]
      }],
      flatten([for profile in data.aws_bedrock_inference_profile.nestbot : [
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
