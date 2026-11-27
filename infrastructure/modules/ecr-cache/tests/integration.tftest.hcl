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
    Environment = "test"
    Project     = "nest"
  }
  name = "nest-test-backend-cache"
}

run "ecr_cache_integration_apply" {
  command = apply

  assert {
    condition     = aws_ecr_repository.main.name == var.name
    error_message = "ECR cache repository name must match the configured name."
  }

  assert {
    condition     = aws_ecr_repository.main.image_tag_mutability == "MUTABLE"
    error_message = "ECR cache repository must allow mutable tags for build cache manifests."
  }

  assert {
    condition     = aws_ecr_repository.main.image_scanning_configuration[0].scan_on_push == false
    error_message = "ECR cache repository image scanning on push must be disabled."
  }

  assert {
    condition     = aws_ecr_lifecycle_policy.main.repository == aws_ecr_repository.main.name
    error_message = "ECR lifecycle policy repository name does not match."
  }
}
