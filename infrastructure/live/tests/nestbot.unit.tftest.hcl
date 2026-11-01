mock_provider "aws" {
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
    condition     = length(module.nestbot) == 1 && length(module.nestbot_build_cache) == 1 && output.nestbot_service_name == "nest-staging-nestbot-service"
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
    condition     = length(module.nestbot) == 1 && length(module.nestbot_build_cache) == 1 && output.nestbot_service_name == "nest-staging-nestbot-service"
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
    condition     = length(module.nestbot) == 0 && length(module.nestbot_build_cache) == 0 && length(local.backend_environment_variables) == 0
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
