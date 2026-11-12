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
  mock_data "aws_iam_policy_document" {
    defaults = {
      json = "{\"Version\":\"2012-10-17\",\"Statement\":[]}"
    }
  }
}
mock_provider "random" {}

variables {
  backend_image_tag      = "test-backend"
  django_configuration   = "Staging"
  django_settings_module = "settings.staging"
  domain_name            = "nest.owasp.dev"
  enable_cron_tasks      = false
  environment            = "staging"
  frontend_image_tag     = "test-frontend"
  nestbot_image_tag      = "test-nestbot"
}

run "test_nestbot_provisioned_in_staging" {
  command = plan

  assert {
    condition     = length(module.nestbot) == 1 && length(module.nestbot_worker) == 1 && length(module.nestbot_build_cache) == 1 && output.nestbot_service_name == "nest-staging-nestbot-service"
    error_message = "Staging must provision NestBot without an enable flag."
  }

  assert {
    condition     = !output.route_slack_to_nestbot && length(local.backend_environment_variables) == 0 && contains(keys(local.backend_parameters_arns), "DJANGO_SLACK_BOT_TOKEN")
    error_message = "Backend Slack must remain configured until cutover."
  }
}

run "test_nestbot_bootstrap" {
  command = plan

  variables {
    nestbot_desired_count = 0
    nestbot_image_tag     = "first-image"
  }

  assert {
    condition     = length(module.nestbot) == 1 && length(module.nestbot_worker) == 1 && length(module.nestbot_build_cache) == 1 && output.nestbot_service_name == "nest-staging-nestbot-service"
    error_message = "Bootstrap must provision the NestBot module with its own service name."
  }

  assert {
    condition     = length(local.backend_environment_variables) == 0 && contains(keys(local.backend_parameters_arns), "DJANGO_SLACK_SIGNING_SECRET")
    error_message = "Provisioning NestBot must not disable backend Slack before cutover."
  }

  assert {
    condition     = contains(keys(module.parameters.nestbot_ssm_parameter_arns), "DJANGO_GOOGLE_API_KEY")
    error_message = "Staging must provision NestBot's Google parameter."
  }
}

run "test_nestbot_slack_cutover" {
  command = plan

  variables {
    nestbot_image_tag      = "first-image"
    route_slack_to_nestbot = true
  }

  assert {
    condition     = output.route_slack_to_nestbot && local.backend_environment_variables == tomap({ DJANGO_SLACK_BOT_TOKEN = "", DJANGO_SLACK_SIGNING_SECRET = "" })
    error_message = "Backend Slack must be disabled explicitly at cutover."
  }

  assert {
    condition     = !contains(keys(local.backend_parameters_arns), "DJANGO_SLACK_BOT_TOKEN") && !contains(keys(local.backend_parameters_arns), "DJANGO_SLACK_SIGNING_SECRET")
    error_message = "Backend Slack variables must not also be injected as secrets."
  }

  assert {
    condition     = contains(keys(local.backend_parameters_arns), "DJANGO_DB_PASSWORD") && contains(keys(module.parameters.django_ssm_parameter_arns), "DJANGO_SLACK_BOT_TOKEN")
    error_message = "Cutover must preserve DB credentials and the shared Slack parameters used by NestBot."
  }
}

run "test_production_defaults_remain_disabled" {
  command = plan

  variables {
    django_configuration   = "Production"
    django_settings_module = "settings.production"
    environment            = "production"
    nestbot_image_tag      = ""
  }

  assert {
    condition     = length(module.nestbot) == 0 && length(module.nestbot_worker) == 0 && length(aws_iam_policy.nestbot_bedrock) == 0 && length(module.nestbot_build_cache) == 0 && length(local.backend_environment_variables) == 0
    error_message = "Production must retain its existing services."
  }

  assert {
    condition     = contains(keys(local.backend_parameters_arns), "DJANGO_SLACK_BOT_TOKEN") && contains(keys(local.backend_parameters_arns), "DJANGO_SLACK_SIGNING_SECRET")
    error_message = "Production must retain both Slack credentials on the backend."
  }
}

run "test_reject_production_routing" {
  command = plan

  variables {
    environment            = "production"
    route_slack_to_nestbot = true
  }

  expect_failures = [var.route_slack_to_nestbot]
}

run "test_reject_routing_without_running_tasks" {
  command = plan

  variables {
    nestbot_desired_count  = 0
    nestbot_image_tag      = "test-image"
    route_slack_to_nestbot = true
  }

  expect_failures = [var.route_slack_to_nestbot]
}

run "test_reject_missing_nestbot_image" {
  command = plan

  variables {
    nestbot_image_tag = ""
  }

  expect_failures = [var.nestbot_image_tag]
}

run "test_staging_ai_defaults_enabled" {
  command = plan

  assert {
    condition     = var.nestbot_ai_assistant_enabled && output.nestbot_worker_service_name == "nest-staging-nestbot-worker-service"
    error_message = "Staging must provision an AI worker with AI enabled by default."
  }
}

run "test_ai_switch_independent_of_routing" {
  command = plan

  variables {
    nestbot_ai_assistant_enabled = true
    route_slack_to_nestbot       = false
  }

  assert {
    condition     = var.nestbot_ai_assistant_enabled && !output.route_slack_to_nestbot
    error_message = "Enabling AI must not change Slack routing."
  }

  assert {
    condition     = module.nestbot[0].container_environment.DJANGO_NESTBOT_AI_ASSISTANT_ENABLED == "true" && module.nestbot_worker[0].container_environment.DJANGO_NESTBOT_AI_ASSISTANT_ENABLED == "true"
    error_message = "Both NestBot containers must receive AI true independently of routing."
  }
}

run "test_ai_can_be_disabled_without_changing_routing" {
  command = plan

  variables {
    nestbot_ai_assistant_enabled = false
    route_slack_to_nestbot       = true
  }

  assert {
    condition     = !var.nestbot_ai_assistant_enabled && output.route_slack_to_nestbot
    error_message = "Disabling AI must preserve separately configured Slack routing."
  }

  assert {
    condition     = module.nestbot[0].container_environment.DJANGO_NESTBOT_AI_ASSISTANT_ENABLED == "false" && module.nestbot_worker[0].container_environment.DJANGO_NESTBOT_AI_ASSISTANT_ENABLED == "false"
    error_message = "Both NestBot containers must receive AI false independently of routing."
  }
}

run "test_bedrock_configuration" {
  command = plan

  override_resource {
    target          = aws_iam_policy.nestbot_bedrock[0]
    override_during = plan
    values = {
      arn = "arn:aws:iam::123456789012:policy/nest-staging-nestbot-bedrock"
    }
  }

  variables {
    nestbot_llm_provider       = "bedrock"
    nestbot_bedrock_model_name = "amazon.nova-lite-v1:0"
    aws_region                 = "eu-west-1"
  }

  assert {
    condition     = local.nestbot_environment_variables.LLM_PROVIDER == "bedrock" && local.nestbot_environment_variables.BEDROCK_MODEL_NAME == "amazon.nova-lite-v1:0" && local.nestbot_environment_variables.AWS_DEFAULT_REGION == "eu-west-1" && local.nestbot_environment_variables.EMBEDDING_PROVIDER == "google"
    error_message = "Bedrock answer configuration must preserve Google embeddings and use the configured region."
  }

  assert {
    condition     = contains(module.nestbot[0].additional_task_role_policy_arns, aws_iam_policy.nestbot_bedrock[0].arn)
    error_message = "The approved Bedrock policy must be attached to the NestBot application task role."
  }
}

run "test_bedrock_requires_model" {
  command = plan
  variables {
    nestbot_llm_provider = "bedrock"
  }
  expect_failures = [var.nestbot_bedrock_model_name]
}

run "test_reject_invalid_bedrock_target_type" {
  command = plan
  variables {
    nestbot_bedrock_target_type = "unsupported"
  }
  expect_failures = [var.nestbot_bedrock_target_type]
}

run "test_reject_invalid_llm_provider" {
  command = plan
  variables {
    nestbot_llm_provider = "unsupported"
  }
  expect_failures = [var.nestbot_llm_provider]
}

run "test_bedrock_foundation_model_policy" {
  command = plan
  variables {
    nestbot_llm_provider       = "bedrock"
    nestbot_bedrock_model_name = "amazon.nova-lite-v1:0"
  }
  assert {
    condition = jsondecode(aws_iam_policy.nestbot_bedrock[0].policy).Statement == [{
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
    nestbot_llm_provider        = "bedrock"
    nestbot_bedrock_target_type = "inference-profile"
    nestbot_bedrock_model_name  = "eu.amazon.nova-lite-v1:0"
  }
  assert {
    condition     = jsondecode(aws_iam_policy.nestbot_bedrock[0].policy).Statement[0].Resource == [data.aws_bedrock_inference_profile.nestbot[0].inference_profile_arn] && jsondecode(aws_iam_policy.nestbot_bedrock[0].policy).Statement[0].Action == ["bedrock:InvokeModel", "bedrock:GetInferenceProfile"]
    error_message = "Profile invocation and lookup must be restricted to the selected profile."
  }
  assert {
    condition     = toset(jsondecode(aws_iam_policy.nestbot_bedrock[0].policy).Statement[1].Resource) == toset([for model in data.aws_bedrock_inference_profile.nestbot[0].models : model.model_arn]) && jsondecode(aws_iam_policy.nestbot_bedrock[0].policy).Statement[1].Condition.StringEquals["bedrock:InferenceProfileArn"] == data.aws_bedrock_inference_profile.nestbot[0].inference_profile_arn
    error_message = "All destination models must be allowed only through the selected profile."
  }
}

run "test_google_has_no_bedrock_resources" {
  command = plan
  assert {
    condition     = length(aws_iam_policy.nestbot_bedrock) == 0 && length(data.aws_bedrock_foundation_model.nestbot) == 0 && length(data.aws_bedrock_inference_profile.nestbot) == 0
    error_message = "Google must not create Bedrock policies or look up Bedrock targets."
  }

}
