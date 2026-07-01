provider "aws" {
  access_key                  = "test"
  region                      = "us-east-1"
  s3_use_path_style           = true
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    iam = "http://localhost:4566"
    kms = "http://localhost:4566"
    s3  = "http://localhost:4566"
    ssm = "http://localhost:4566"
    sts = "http://localhost:4566"
  }
}

variables {
  common_tags                   = { Environment = "staging", Project = "nest" }
  db_password_arn               = "arn:aws:ssm:us-east-1:000000000000:parameter/nest/staging/DJANGO_DB_PASSWORD"
  django_allowed_hosts          = "nest.owasp.dev"
  django_allowed_origins        = "https://nest.owasp.dev"
  django_aws_static_bucket_name = "nest-staging-static-abcd1234"
  django_configuration          = "Staging"
  django_db_host                = "db.example.com"
  django_db_name                = "nest_db"
  django_db_port                = "5432"
  django_db_user                = "nest_user"
  django_redis_host             = "redis.example.com"
  django_release_version        = "1.0.0"
  django_settings_module        = "settings.staging"
  environment                   = "staging"
  next_server_csrf_url          = "https://nest.owasp.dev/csrf"
  next_server_graphql_url       = "https://nest.owasp.dev/graphql"
  nextauth_url                  = "https://nest.owasp.dev"
  project_name                  = "nest"
  redis_password_arn            = "arn:aws:ssm:us-east-1:000000000000:parameter/nest/staging/DJANGO_REDIS_PASSWORD"
  slack_bot_token_suffix        = "T00000000X"
}

run "smoke_staging_parameters" {
  command = apply

  assert {
    condition     = aws_ssm_parameter.django_allowed_hosts.name == "/nest/staging/DJANGO_ALLOWED_HOSTS"
    error_message = "SSM parameter path must follow /nest/staging/DJANGO_ALLOWED_HOSTS format."
  }

  assert {
    condition     = aws_ssm_parameter.django_configuration.name == "/nest/staging/DJANGO_CONFIGURATION"
    error_message = "SSM parameter path must follow /nest/staging/DJANGO_CONFIGURATION format."
  }

  assert {
    condition     = aws_ssm_parameter.django_configuration.value == "Staging"
    error_message = "DJANGO_CONFIGURATION value must be Staging for staging environment."
  }

  assert {
    condition     = aws_ssm_parameter.django_settings_module.name == "/nest/staging/DJANGO_SETTINGS_MODULE"
    error_message = "SSM parameter path must follow /nest/staging/DJANGO_SETTINGS_MODULE format."
  }

  assert {
    condition     = aws_ssm_parameter.django_settings_module.value == "settings.staging"
    error_message = "DJANGO_SETTINGS_MODULE must be settings.staging for staging environment."
  }

  assert {
    condition     = aws_ssm_parameter.django_release_version.name == "/nest/staging/DJANGO_RELEASE_VERSION"
    error_message = "SSM parameter path must follow /nest/staging/DJANGO_RELEASE_VERSION format."
  }

  assert {
    condition     = aws_ssm_parameter.django_secret_key.type == "SecureString"
    error_message = "DJANGO_SECRET_KEY must be SecureString type."
  }
}
