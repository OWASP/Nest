terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}-cluster"
  tags = var.common_tags
}

resource "aws_ecr_repository" "main" {
  name = "${var.project_name}-${var.environment}-backend"
  tags = var.common_tags
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

resource "aws_iam_role_policy_attachment" "ecs_tasks_execution_role_policy" {
  role       = aws_iam_role.ecs_tasks_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "ecs_tasks_fixtures_s3_access" {
  role       = aws_iam_role.ecs_tasks_execution_role.name
  policy_arn = var.fixtures_read_only_policy_arn
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

resource "aws_iam_role_policy_attachment" "event_bridge_role_policy" {
  role       = aws_iam_role.event_bridge_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceEventsRole"
}

module "sync_data_task" {
  source = "./modules/task"

  aws_region                   = var.aws_region
  command                      = ["python", "manage.py", "sync-data"]
  common_tags                  = var.common_tags
  container_environment        = var.django_environment_variables
  cpu                          = var.sync_data_task_cpu
  ecs_cluster_arn              = aws_ecs_cluster.main.arn
  ecs_tasks_execution_role_arn = aws_iam_role.ecs_tasks_execution_role.arn
  environment                  = var.environment
  event_bridge_role_arn        = aws_iam_role.event_bridge_role.arn
  image_url                    = aws_ecr_repository.main.repository_url
  memory                       = var.sync_data_task_memory
  private_subnet_ids           = var.private_subnet_ids
  project_name                 = var.project_name
  schedule_expression          = "cron(17 05 * * ? *)"
  security_group_ids           = [var.lambda_sg_id]
  task_name                    = "sync-data"
}

module "owasp_update_project_health_metrics_task" {
  source = "./modules/task"

  aws_region                   = var.aws_region
  command                      = ["/bin/sh", "-c", "python manage.py owasp-update-project-health-requirements && python manage.py owasp-update-project-health-metrics"]
  common_tags                  = var.common_tags
  container_environment        = var.django_environment_variables
  cpu                          = var.update_project_health_metrics_task_cpu
  ecs_cluster_arn              = aws_ecs_cluster.main.arn
  ecs_tasks_execution_role_arn = aws_iam_role.ecs_tasks_execution_role.arn
  environment                  = var.environment
  event_bridge_role_arn        = aws_iam_role.event_bridge_role.arn
  image_url                    = aws_ecr_repository.main.repository_url
  memory                       = var.update_project_health_metrics_task_memory
  private_subnet_ids           = var.private_subnet_ids
  project_name                 = var.project_name
  schedule_expression          = "cron(17 17 * * ? *)"
  security_group_ids           = [var.lambda_sg_id]
  task_name                    = "owasp-update-project-health-metrics"
}

module "owasp_update_project_health_scores_task" {
  source = "./modules/task"

  aws_region                   = var.aws_region
  command                      = ["python", "manage.py", "owasp-update-project-health-scores"]
  common_tags                  = var.common_tags
  container_environment        = var.django_environment_variables
  cpu                          = var.update_project_health_scores_task_cpu
  ecs_cluster_arn              = aws_ecs_cluster.main.arn
  ecs_tasks_execution_role_arn = aws_iam_role.ecs_tasks_execution_role.arn
  environment                  = var.environment
  event_bridge_role_arn        = aws_iam_role.event_bridge_role.arn
  image_url                    = aws_ecr_repository.main.repository_url
  memory                       = var.update_project_health_scores_task_memory
  private_subnet_ids           = var.private_subnet_ids
  project_name                 = var.project_name
  schedule_expression          = "cron(22 17 * * ? *)"
  security_group_ids           = [var.lambda_sg_id]
  task_name                    = "owasp-update-project-health-scores"
}

module "migrate_task" {
  source = "./modules/task"

  aws_region                   = var.aws_region
  command                      = ["python", "manage.py", "migrate"]
  common_tags                  = var.common_tags
  container_environment        = var.django_environment_variables
  cpu                          = var.migrate_task_cpu
  ecs_cluster_arn              = aws_ecs_cluster.main.arn
  ecs_tasks_execution_role_arn = aws_iam_role.ecs_tasks_execution_role.arn
  environment                  = var.environment
  image_url                    = "${aws_ecr_repository.main.repository_url}:latest"
  memory                       = var.migrate_task_memory
  private_subnet_ids           = var.private_subnet_ids
  project_name                 = var.project_name
  security_group_ids           = [var.lambda_sg_id]
  task_name                    = "migrate"
}

module "load_data_task" {
  source = "./modules/task"

  aws_region                   = var.aws_region
  command                      = ["/bin/sh", "-c", "aws s3 cp s3://${var.fixtures_s3_bucket}/nest.json.gz /data/nest.json.gz && python manage.py load_data --file /data/nest.json.gz"]
  common_tags                  = var.common_tags
  container_environment        = var.django_environment_variables
  cpu                          = var.load_data_task_cpu
  ecs_cluster_arn              = aws_ecs_cluster.main.arn
  ecs_tasks_execution_role_arn = aws_iam_role.ecs_tasks_execution_role.arn
  environment                  = var.environment
  image_url                    = "${aws_ecr_repository.main.repository_url}:latest"
  memory                       = var.load_data_task_memory
  private_subnet_ids           = var.private_subnet_ids
  project_name                 = var.project_name
  security_group_ids           = [var.lambda_sg_id]
  task_name                    = "load-data"
}

module "index_data_task" {
  source = "./modules/task"

  aws_region = var.aws_region
  command = [
    "/bin/sh",
    "-c",
    <<-EOT
    python manage.py algolia_reindex
    python manage.py algolia_update_replicas
    python manage.py algolia_update_synonyms
    EOT
  ]
  common_tags                  = var.common_tags
  container_environment        = var.django_environment_variables
  cpu                          = var.index_data_task_cpu
  ecs_cluster_arn              = aws_ecs_cluster.main.arn
  ecs_tasks_execution_role_arn = aws_iam_role.ecs_tasks_execution_role.arn
  environment                  = var.environment
  image_url                    = "${aws_ecr_repository.main.repository_url}:latest"
  memory                       = var.index_data_task_memory
  private_subnet_ids           = var.private_subnet_ids
  project_name                 = var.project_name
  security_group_ids           = [var.lambda_sg_id]
  task_name                    = "index-data"
}
