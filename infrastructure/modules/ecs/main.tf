terraform {
  required_version = "1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.22.0"
    }
  }
}

data "aws_caller_identity" "current" {}

resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}-tasks-cluster"
  tags = var.common_tags
}

resource "aws_ecs_cluster_capacity_providers" "main" {
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]
  cluster_name       = aws_ecs_cluster.main.name

  default_capacity_provider_strategy {
    base              = 0
    capacity_provider = var.use_fargate_spot ? "FARGATE_SPOT" : "FARGATE"
    weight            = 1
  }
}

resource "aws_ecr_lifecycle_policy" "main" {
  repository = aws_ecr_repository.main.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Remove untagged images"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 7
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# TODO: disallow tag mutability
# nosemgrep: terraform.aws.security.aws-ecr-mutable-image-tags.aws-ecr-mutable-image-tags
resource "aws_ecr_repository" "main" {
  name                 = "${var.project_name}-${var.environment}-backend"
  image_tag_mutability = "MUTABLE"
  tags                 = var.common_tags

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_iam_role" "ecs_tasks_execution_role" {
  name = "${var.project_name}-${var.environment}-ecs-tasks-execution-role"
  tags = var.common_tags

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}


resource "aws_iam_policy" "ecs_tasks_execution_role_ssm_policy" {
  name        = "${var.project_name}-${var.environment}-ecs-tasks-ssm-policy"
  description = "Allow ECS tasks to read SSM parameters"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ssm:GetParameters"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/${var.project_name}/${var.environment}/*"
      }
    ]
  })
  tags = var.common_tags
}

resource "aws_iam_policy" "ecs_tasks_execution_policy" {
  name        = "${var.project_name}-${var.environment}-ecs-tasks-execution-policy"
  description = "Custom policy for ECS task execution - ECR and CloudWatch Logs access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ecr:GetAuthorizationToken"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer"
        ]
        Effect   = "Allow"
        Resource = aws_ecr_repository.main.arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/ecs/${var.project_name}-${var.environment}-*:*"
      }
    ]
  })
  tags = var.common_tags
}

resource "aws_iam_role_policy_attachment" "ecs_tasks_execution_policy_attachment" {
  policy_arn = aws_iam_policy.ecs_tasks_execution_policy.arn
  role       = aws_iam_role.ecs_tasks_execution_role.name
}

resource "aws_iam_role_policy_attachment" "ecs_tasks_execution_role_ssm_policy_attachment" {
  policy_arn = aws_iam_policy.ecs_tasks_execution_role_ssm_policy.arn
  role       = aws_iam_role.ecs_tasks_execution_role.name
}

resource "aws_iam_role" "ecs_task_role" {
  name = "${var.project_name}-${var.environment}-ecs-task-role"
  tags = var.common_tags

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_role_fixtures_s3_access" {
  policy_arn = var.fixtures_read_only_policy_arn
  role       = aws_iam_role.ecs_task_role.name
}

resource "aws_iam_role" "event_bridge_role" {
  name = "${var.project_name}-${var.environment}-event-bridge-role"
  tags = var.common_tags

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "event_bridge_ecs_policy" {
  name        = "${var.project_name}-${var.environment}-event-bridge-ecs-policy"
  description = "Allow EventBridge to run ECS tasks"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "ecs:RunTask"
        Effect = "Allow"
        Condition = {
          ArnLike = {
            "ecs:cluster" = aws_ecs_cluster.main.arn
          }
        }
        Resource = "arn:aws:ecs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:task-definition/${var.project_name}-${var.environment}-*:*"
      },
      {
        Action = "iam:PassRole"
        Effect = "Allow"
        Resource = [
          aws_iam_role.ecs_task_role.arn,
          aws_iam_role.ecs_tasks_execution_role.arn
        ]
      }
    ]
  })
  tags = var.common_tags
}

resource "aws_iam_role_policy_attachment" "event_bridge_policy_attachment" {
  policy_arn = aws_iam_policy.event_bridge_ecs_policy.arn
  role       = aws_iam_role.event_bridge_role.name
}

module "sync_data_task" {
  source = "./modules/task"

  assign_public_ip             = var.assign_public_ip
  aws_region                   = var.aws_region
  command                      = ["/bin/sh", "-c", "EXEC_MODE=direct make sync-data"]
  common_tags                  = var.common_tags
  container_parameters_arns    = var.container_parameters_arns
  cpu                          = var.sync_data_task_cpu
  ecs_cluster_arn              = aws_ecs_cluster.main.arn
  ecs_tasks_execution_role_arn = aws_iam_role.ecs_tasks_execution_role.arn
  environment                  = var.environment
  event_bridge_role_arn        = aws_iam_role.event_bridge_role.arn
  image_url                    = "${aws_ecr_repository.main.repository_url}:${var.image_tag}"
  memory                       = var.sync_data_task_memory
  project_name                 = var.project_name
  schedule_expression          = "cron(17 05 * * ? *)"
  security_group_ids           = [var.ecs_sg_id]
  subnet_ids                   = var.subnet_ids
  task_name                    = "sync-data"
  use_fargate_spot             = var.use_fargate_spot
}

module "owasp_update_project_health_metrics_task" {
  source = "./modules/task"

  assign_public_ip = var.assign_public_ip
  aws_region       = var.aws_region
  command = [
    "/bin/sh",
    "-c",
    <<-EOT
    set -e
    EXEC_MODE=direct make owasp-update-project-health-requirements
    EXEC_MODE=direct make owasp-update-project-health-metrics
    EOT
  ]
  common_tags                  = var.common_tags
  container_parameters_arns    = var.container_parameters_arns
  cpu                          = var.update_project_health_metrics_task_cpu
  ecs_cluster_arn              = aws_ecs_cluster.main.arn
  ecs_tasks_execution_role_arn = aws_iam_role.ecs_tasks_execution_role.arn
  environment                  = var.environment
  event_bridge_role_arn        = aws_iam_role.event_bridge_role.arn
  image_url                    = "${aws_ecr_repository.main.repository_url}:${var.image_tag}"
  memory                       = var.update_project_health_metrics_task_memory
  project_name                 = var.project_name
  schedule_expression          = "cron(17 17 * * ? *)"
  security_group_ids           = [var.ecs_sg_id]
  subnet_ids                   = var.subnet_ids
  task_name                    = "owasp-update-project-health-metrics"
  use_fargate_spot             = var.use_fargate_spot
}

module "owasp_update_project_health_scores_task" {
  source = "./modules/task"

  assign_public_ip             = var.assign_public_ip
  aws_region                   = var.aws_region
  command                      = ["/bin/sh", "-c", "EXEC_MODE=direct make owasp-update-project-health-scores"]
  common_tags                  = var.common_tags
  container_parameters_arns    = var.container_parameters_arns
  cpu                          = var.update_project_health_scores_task_cpu
  ecs_cluster_arn              = aws_ecs_cluster.main.arn
  ecs_tasks_execution_role_arn = aws_iam_role.ecs_tasks_execution_role.arn
  environment                  = var.environment
  event_bridge_role_arn        = aws_iam_role.event_bridge_role.arn
  image_url                    = "${aws_ecr_repository.main.repository_url}:${var.image_tag}"
  memory                       = var.update_project_health_scores_task_memory
  project_name                 = var.project_name
  schedule_expression          = "cron(22 17 * * ? *)"
  security_group_ids           = [var.ecs_sg_id]
  subnet_ids                   = var.subnet_ids
  task_name                    = "owasp-update-project-health-scores"
  use_fargate_spot             = var.use_fargate_spot
}

module "migrate_task" {
  source = "./modules/task"

  assign_public_ip             = var.assign_public_ip
  aws_region                   = var.aws_region
  command                      = ["/bin/sh", "-c", "EXEC_MODE=direct make migrate"]
  common_tags                  = var.common_tags
  container_parameters_arns    = var.container_parameters_arns
  cpu                          = var.migrate_task_cpu
  ecs_cluster_arn              = aws_ecs_cluster.main.arn
  ecs_tasks_execution_role_arn = aws_iam_role.ecs_tasks_execution_role.arn
  environment                  = var.environment
  image_url                    = "${aws_ecr_repository.main.repository_url}:${var.image_tag}"
  memory                       = var.migrate_task_memory
  project_name                 = var.project_name
  security_group_ids           = [var.ecs_sg_id]
  subnet_ids                   = var.subnet_ids
  task_name                    = "migrate"
  use_fargate_spot             = false
}

module "load_data_task" {
  source = "./modules/task"

  assign_public_ip = var.assign_public_ip
  aws_region       = var.aws_region
  command = [
    "/bin/sh",
    "-c",
    <<-EOT
    set -e
    python -c "
    import boto3
    s3 = boto3.client('s3')
    s3.download_file('${var.fixtures_bucket_name}', 'nest.json.gz', '/tmp/nest.json.gz')
    "
    python manage.py load_data --fixture-path /tmp/nest.json.gz
    EOT
  ]
  common_tags                  = var.common_tags
  container_parameters_arns    = var.container_parameters_arns
  cpu                          = var.load_data_task_cpu
  ecs_cluster_arn              = aws_ecs_cluster.main.arn
  ecs_tasks_execution_role_arn = aws_iam_role.ecs_tasks_execution_role.arn
  environment                  = var.environment
  image_url                    = "${aws_ecr_repository.main.repository_url}:${var.image_tag}"
  memory                       = var.load_data_task_memory
  project_name                 = var.project_name
  security_group_ids           = [var.ecs_sg_id]
  subnet_ids                   = var.subnet_ids
  task_name                    = "load-data"
  task_role_arn                = aws_iam_role.ecs_task_role.arn
  use_fargate_spot             = false
}

module "index_data_task" {
  source = "./modules/task"

  assign_public_ip             = var.assign_public_ip
  aws_region                   = var.aws_region
  command                      = ["/bin/sh", "-c", "EXEC_MODE=direct make index-data"]
  common_tags                  = var.common_tags
  container_parameters_arns    = var.container_parameters_arns
  cpu                          = var.index_data_task_cpu
  ecs_cluster_arn              = aws_ecs_cluster.main.arn
  ecs_tasks_execution_role_arn = aws_iam_role.ecs_tasks_execution_role.arn
  environment                  = var.environment
  image_url                    = "${aws_ecr_repository.main.repository_url}:${var.image_tag}"
  memory                       = var.index_data_task_memory
  project_name                 = var.project_name
  security_group_ids           = [var.ecs_sg_id]
  subnet_ids                   = var.subnet_ids
  task_name                    = "index-data"
  use_fargate_spot             = false
}
