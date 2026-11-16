mock_provider "aws" {
  mock_data "aws_bedrock_foundation_model" {
    defaults = {
      model_arn = "arn:aws:bedrock:eu-west-1::foundation-model/amazon.nova-lite-v1:0"
    }
  }
  mock_data "aws_bedrock_inference_profile" {
    defaults = {
      inference_profile_arn = "arn:aws:bedrock:eu-west-1:123456789012:inference-profile/eu.amazon.nova-lite-v1:0"
      models = [
        { model_arn = "arn:aws:bedrock:eu-west-1::foundation-model/amazon.nova-lite-v1:0" },
        { model_arn = "arn:aws:bedrock:eu-central-1::foundation-model/amazon.nova-lite-v1:0" },
      ]
    }
  }
}

variables {
  common_tags = { Environment = "test", Project = "nest" }
  model_name  = "amazon.nova-lite-v1:0"
  name_prefix = "nest-staging-nestbot"
}

run "test_bedrock_foundation_model_policy" {
  command = plan
  variables {
    model_name = "amazon.nova-lite-v1:0"
  }
  assert {
    condition = jsondecode(aws_iam_policy.main.policy).Statement == [{
      Effect   = "Allow"
      Action   = ["bedrock:InvokeModel"]
      Resource = ["arn:aws:bedrock:eu-west-1::foundation-model/amazon.nova-lite-v1:0"]
    }]
    error_message = "Direct invocation must be restricted to the selected foundation model."
  }
}

run "test_bedrock_inference_profile_policy" {
  command = plan
  variables {
    target_type = "inference-profile"
    model_name  = "eu.amazon.nova-lite-v1:0"
  }
  assert {
    condition     = length(jsondecode(aws_iam_policy.main.policy).Statement) == 2 && jsondecode(aws_iam_policy.main.policy).Statement[0].Resource == [data.aws_bedrock_inference_profile.main[0].inference_profile_arn] && jsondecode(aws_iam_policy.main.policy).Statement[0].Action == ["bedrock:InvokeModel", "bedrock:GetInferenceProfile"]
    error_message = "The policy must contain exactly two statements, with profile invocation and lookup restricted to the selected profile."
  }
  assert {
    condition     = toset(jsondecode(aws_iam_policy.main.policy).Statement[1].Resource) == toset([for model in data.aws_bedrock_inference_profile.main[0].models : model.model_arn]) && jsondecode(aws_iam_policy.main.policy).Statement[1].Condition.StringEquals["bedrock:InferenceProfileArn"] == data.aws_bedrock_inference_profile.main[0].inference_profile_arn
    error_message = "All destination models must be allowed only through the selected profile."
  }
}

run "test_reject_empty_model" {
  command = plan
  variables {
    model_name = " "
  }
  expect_failures = [var.model_name]
}

run "test_reject_invalid_target_type" {
  command = plan
  variables {
    target_type = "unsupported"
  }
  expect_failures = [var.target_type]
}
