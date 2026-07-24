provider "aws" {
  access_key                  = "test"
  region                      = "us-east-1"
  s3_use_path_style           = true
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
}

variables {
  common_tags = {
    Environment = "staging"
    Project     = "nest"
  }
  name = "nest-staging-backend-cache"
}

run "smoke_staging_ecr_backend_cache" {
  command = apply

  assert {
    condition     = aws_ecr_repository.main.name == var.name
    error_message = "ECR cache repo name must be nest-staging-backend-cache."
  }

  assert {
    condition     = aws_ecr_repository.main.image_tag_mutability == "MUTABLE"
    error_message = "ECR cache repo must allow mutable tags."
  }

  assert {
    condition     = aws_ecr_repository.main.image_scanning_configuration[0].scan_on_push == false
    error_message = "ECR cache repo must not scan on push."
  }

  assert {
    condition     = aws_ecr_lifecycle_policy.main.repository == var.name
    error_message = "Lifecycle policy must be attached to nest-staging-backend-cache."
  }
}
