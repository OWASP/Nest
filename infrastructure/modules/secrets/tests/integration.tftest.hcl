provider "aws" {
  access_key                  = "test"
  region                      = "us-east-1"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
}

variables {
  common_tags                    = { Environment = "test", Project = "nest" }
  django_secret_key              = "existing-django-secret-key"
  environment                    = "test"
  kms_key_arn                    = "arn:aws:kms:us-east-1:000000000000:key/12345678-1234-1234-1234-123456789012"
  nextauth_secret                = "existing-nextauth-secret"
  project_name                   = "nest"
  secret_recovery_window_in_days = 0
  slack_bot_token_suffix         = "T04T40NHX"
}

run "provision_pr1_common" {
  command   = apply
  state_key = "pr1_handoff_common"

  module {
    source = "./tests/fixtures/pr1"
  }

  variables {
    external_secret_values = {
      DJANGO_ALGOLIA_WRITE_API_KEY     = "existing-algolia-write-key"
      DJANGO_OPEN_AI_SECRET_KEY        = "existing-openai-key"
      DJANGO_SENTRY_DSN                = "existing-sentry-dsn"
      DJANGO_SLACK_BOT_TOKEN           = "existing-slack-token"
      DJANGO_SLACK_SIGNING_SECRET      = "existing-slack-signing-secret"
      GITHUB_TOKEN                     = "existing-github-token"
      NEXT_SERVER_GITHUB_CLIENT_SECRET = "existing-github-client-secret"
      NEST_GITHUB_APP_PRIVATE_KEY      = "existing-github-private-key\nsecond-line\n"
      SLACK_BOT_TOKEN_CUSTOM_WORKSPACE = "existing-workspace-token"
    }
  }
}

run "secrets_integration_handoff_common" {
  command   = apply
  state_key = "pr1_handoff_common"

  assert {
    condition = (
      aws_secretsmanager_secret_version.django_secret_key.secret_string == var.django_secret_key &&
      aws_secretsmanager_secret_version.nextauth_secret.secret_string == var.nextauth_secret &&
      contains(aws_secretsmanager_secret_version.django_secret_key.version_stages, "AWSCURRENT") &&
      contains(aws_secretsmanager_secret_version.nextauth_secret.version_stages, "AWSCURRENT")
    )
    error_message = "Generated credential versions must preserve their supplied values and remain AWSCURRENT."
  }

  assert {
    condition     = length(aws_secretsmanager_secret.external_runtime) == 7
    error_message = "The handoff must retain all external secret containers in the enabled inventory."
  }
}

run "verify_handoff_common" {
  command = apply

  module {
    source = "./tests/fixtures/verify-versions"
  }

  variables {
    credential_names = run.provision_pr1_common.credential_names
  }

  assert {
    condition     = output.credential_versions == run.provision_pr1_common.credential_versions
    error_message = "The handoff must preserve every PR1 AWSCURRENT version identity and value, including generated and optional credentials."
  }
}

run "repeat_plan_after_handoff_common" {
  command   = plan
  state_key = "pr1_handoff_common"

  assert {
    condition = (
      aws_secretsmanager_secret_version.django_secret_key.version_id == run.provision_pr1_common.credential_versions["DJANGO_SECRET_KEY"].version_id &&
      aws_secretsmanager_secret_version.nextauth_secret.version_id == run.provision_pr1_common.credential_versions["NEXTAUTH_SECRET"].version_id
    )
    error_message = "Later plans must preserve the generated secret versions without depending on deleted SSM credentials."
  }
}

run "provision_pr1_optional" {
  command   = apply
  state_key = "pr1_handoff_optional"

  module {
    source = "./tests/fixtures/pr1"
  }

  variables {
    environment               = "test-optional"
    enable_additional_secrets = true
    slack_bot_token_suffix    = "CUSTOM_WORKSPACE"
    external_secret_values = {
      DJANGO_ALGOLIA_WRITE_API_KEY     = "existing-algolia-write-key"
      DJANGO_OPEN_AI_SECRET_KEY        = "existing-openai-key"
      DJANGO_SENTRY_DSN                = "existing-sentry-dsn"
      DJANGO_SLACK_BOT_TOKEN           = "existing-slack-token"
      DJANGO_SLACK_SIGNING_SECRET      = "existing-slack-signing-secret"
      GITHUB_TOKEN                     = "existing-github-token"
      NEXT_SERVER_GITHUB_CLIENT_SECRET = "existing-github-client-secret"
      NEST_GITHUB_APP_PRIVATE_KEY      = "existing-github-private-key\nsecond-line\n"
      SLACK_BOT_TOKEN_CUSTOM_WORKSPACE = "existing-workspace-token"
    }
  }
}

run "secrets_integration_handoff_optional" {
  command   = apply
  state_key = "pr1_handoff_optional"

  variables {
    environment               = "test-optional"
    enable_additional_secrets = true
    slack_bot_token_suffix    = "CUSTOM_WORKSPACE"
  }

  assert {
    condition = (
      aws_secretsmanager_secret_version.django_secret_key.secret_string == var.django_secret_key &&
      aws_secretsmanager_secret_version.nextauth_secret.secret_string == var.nextauth_secret &&
      contains(aws_secretsmanager_secret_version.django_secret_key.version_stages, "AWSCURRENT") &&
      contains(aws_secretsmanager_secret_version.nextauth_secret.version_stages, "AWSCURRENT")
    )
    error_message = "Generated credential versions must preserve their supplied values and remain AWSCURRENT."
  }

  assert {
    condition     = length(aws_secretsmanager_secret.external_runtime) == 9
    error_message = "The handoff must retain all external secret containers in the enabled inventory."
  }
}

run "verify_handoff_optional" {
  command = apply

  module {
    source = "./tests/fixtures/verify-versions"
  }

  variables {
    credential_names = run.provision_pr1_optional.credential_names
  }

  assert {
    condition     = output.credential_versions == run.provision_pr1_optional.credential_versions
    error_message = "The handoff must preserve every PR1 AWSCURRENT version identity and value, including generated and optional credentials."
  }
}

run "repeat_plan_after_handoff_optional" {
  command   = plan
  state_key = "pr1_handoff_optional"

  variables {
    environment               = "test-optional"
    enable_additional_secrets = true
    slack_bot_token_suffix    = "CUSTOM_WORKSPACE"
  }

  assert {
    condition = (
      aws_secretsmanager_secret_version.django_secret_key.version_id == run.provision_pr1_optional.credential_versions["DJANGO_SECRET_KEY"].version_id &&
      aws_secretsmanager_secret_version.nextauth_secret.version_id == run.provision_pr1_optional.credential_versions["NEXTAUTH_SECRET"].version_id
    )
    error_message = "Later plans must preserve the generated secret versions without depending on deleted SSM credentials."
  }
}
