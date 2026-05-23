mock_provider "aws" {}

variables {
  common_tags = {
    Environment = "test"
    Project     = "nest"
  }
  name = "nest-test-backend-cache"
}

run "test_repository_name" {
  command = plan

  assert {
    condition     = aws_ecr_repository.main.name == var.name
    error_message = "ECR cache repository name must match the configured name."
  }
}

run "test_repository_tag_mutability" {
  command = plan

  assert {
    condition     = aws_ecr_repository.main.image_tag_mutability == "MUTABLE"
    error_message = "ECR cache repository must allow mutable tags for build cache manifests."
  }
}

run "test_lifecycle_policy_retains_three_images" {
  command = plan

  assert {
    condition     = jsondecode(aws_ecr_lifecycle_policy.main.policy).rules[0].selection.countNumber == 3
    error_message = "ECR cache lifecycle policy must retain the last 3 images."
  }
}
