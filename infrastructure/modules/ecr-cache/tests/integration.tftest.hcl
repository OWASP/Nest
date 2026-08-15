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
