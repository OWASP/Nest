mock_provider "aws" {}

variables {
  app_security_group_ids = ["sg-backend"]
  aws_region             = "us-east-2"
  common_tags            = { Environment = "test", Project = "nest" }
  environment            = "test"
  kms_key_arn            = "arn:aws:kms:us-east-2:123456789012:key/12345678-1234-1234-1234-123456789012"
  project_name           = "nest"
  subnet_ids             = ["subnet-1", "subnet-2"]
  vm_image               = "victoriametrics/victoria-metrics:v1.145.0@sha256:c014fb5a711d38cb24fd0673197592cd1394bb903dbb16aea565620c9c8a3d70"
  vpc_id                 = "vpc-12345"
}

run "grafana_release_repository" {
  command = plan

  assert {
    condition = (
      aws_ecr_repository.grafana.name == "nest-test-grafana" &&
      aws_ecr_repository.grafana.image_tag_mutability == "IMMUTABLE" &&
      aws_ecr_repository.grafana.image_scanning_configuration[0].scan_on_push
    )
    error_message = "Grafana releases must use the environment-scoped repository, immutable tags, and push scanning."
  }

  assert {
    condition = (
      aws_ecr_lifecycle_policy.grafana.repository == aws_ecr_repository.grafana.name &&
      jsondecode(aws_ecr_lifecycle_policy.grafana.policy).rules[0].selection.countNumber == 7
    )
    error_message = "Grafana must use the project's seven-image retention policy."
  }
}

run "grafana_pull_permissions_are_repository_scoped" {
  command = plan

  override_resource {
    target          = aws_ecr_repository.grafana
    override_during = plan
    values = {
      arn            = "arn:aws:ecr:us-east-2:123456789012:repository/nest-test-grafana"
      repository_url = "123456789012.dkr.ecr.us-east-2.amazonaws.com/nest-test-grafana"
    }
  }

  assert {
    condition = (
      length(jsondecode(aws_iam_policy.grafana_image_pull.policy).Statement) == 2 &&
      jsondecode(aws_iam_policy.grafana_image_pull.policy).Statement[0].Action == "ecr:GetAuthorizationToken" &&
      jsondecode(aws_iam_policy.grafana_image_pull.policy).Statement[0].Resource == "*" &&
      toset(jsondecode(aws_iam_policy.grafana_image_pull.policy).Statement[1].Action) == toset([
        "ecr:BatchCheckLayerAvailability", "ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"
      ]) &&
      jsondecode(aws_iam_policy.grafana_image_pull.policy).Statement[1].Resource == aws_ecr_repository.grafana.arn
    )
    error_message = "Only token authentication may use a wildcard; image access must be pull-only and limited to Grafana's repository."
  }

  assert {
    condition = (
      jsondecode(aws_iam_role.grafana_execution.assume_role_policy).Statement[0].Principal.Service == "ecs-tasks.amazonaws.com" &&
      aws_iam_role_policy_attachment.grafana_image_pull.role == aws_iam_role.grafana_execution.name
    )
    error_message = "Image pull permissions must belong to the dedicated Grafana ECS execution role."
  }

  assert {
    condition = (
      output.grafana_ecr_repository_arn == aws_ecr_repository.grafana.arn &&
      output.grafana_ecr_repository_url == aws_ecr_repository.grafana.repository_url
    )
    error_message = "Repository outputs must identify Grafana's release repository."
  }
}
