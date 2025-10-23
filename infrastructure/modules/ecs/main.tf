terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}-cluster"
  tags = local.common_tags
}

resource "aws_ecr_repository" "main" {
  name = "${var.project_name}-${var.environment}-backend"
  tags = local.common_tags
}

resource "aws_iam_role" "ecs_tasks_execution_role" {
  name = "${var.project_name}-${var.environment}-ecs-tasks-execution-role"
  tags = local.common_tags

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

resource "aws_iam_role" "event_bridge_role" {
  name = "${var.project_name}-${var.environment}-event-bridge-role"
  tags = local.common_tags

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

# Task defitions
resource "aws_ecs_task_definition" "sync_data" {
  family                   = "${var.project_name}-${var.environment}-sync-data"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.sync_data_task_cpu
  memory                   = var.sync_data_task_memory
  execution_role_arn       = aws_iam_role.ecs_tasks_execution_role.arn
  tags                     = local.common_tags

  container_definitions = jsonencode([
    {
      name      = "backend"
      image     = aws_ecr_repository.main.repository_url
      command   = ["python", "manage.py", "sync-data"]
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.sync_data.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

resource "aws_cloudwatch_log_group" "sync_data" {
  name = "/ecs/${var.project_name}-${var.environment}-sync-data"
  tags = local.common_tags
}

resource "aws_cloudwatch_event_rule" "sync_data" {
  name                = "${var.project_name}-${var.environment}-sync-data-rule"
  description         = "Fires daily to trigger the sync-data task"
  schedule_expression = "cron(17 05 * * ? *)"
  tags                = local.common_tags
}

resource "aws_cloudwatch_event_target" "sync_data" {
  rule      = aws_cloudwatch_event_rule.sync_data.name
  target_id = "${var.project_name}-${var.environment}-sync-data-target"
  arn       = aws_ecs_cluster.main.arn

  ecs_target {
    task_definition_arn = aws_ecs_task_definition.sync_data.arn
    launch_type         = "FARGATE"
    network_configuration {
      subnets          = var.private_subnet_ids
      security_groups  = [var.lambda_sg_id]
      assign_public_ip = false
    }
  }

  role_arn = aws_iam_role.event_bridge_role.arn
}

resource "aws_ecs_task_definition" "owasp_update_project_health_metrics" {
  family                   = "${var.project_name}-${var.environment}-owasp-update-project-health-metrics"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.update_project_health_metrics_task_cpu
  memory                   = var.update_project_health_metrics_task_memory
  execution_role_arn       = aws_iam_role.ecs_tasks_execution_role.arn
  tags                     = local.common_tags

  container_definitions = jsonencode([
    {
      name      = "backend"
      image     = aws_ecr_repository.main.repository_url
      command   = ["/bin/sh", "-c", "python manage.py owasp-update-project-health-requirements && python manage.py owasp-update-project-health-metrics"]
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.owasp_update_project_health_metrics.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

resource "aws_cloudwatch_log_group" "owasp_update_project_health_metrics" {
  name = "/ecs/${var.project_name}-${var.environment}-owasp-update-project-health-metrics"
  tags = local.common_tags
}

resource "aws_cloudwatch_event_rule" "owasp_update_project_health_metrics" {
  name                = "${var.project_name}-${var.environment}-owasp-update-project-health-metrics-rule"
  description         = "Fires daily to trigger the owasp-update-project-health-metrics task"
  schedule_expression = "cron(17 17 * * ? *)"
  tags                = local.common_tags
}

resource "aws_cloudwatch_event_target" "owasp_update_project_health_metrics" {
  rule      = aws_cloudwatch_event_rule.owasp_update_project_health_metrics.name
  target_id = "${var.project_name}-${var.environment}-owasp-update-project-health-metrics-target"
  arn       = aws_ecs_cluster.main.arn

  ecs_target {
    task_definition_arn = aws_ecs_task_definition.owasp_update_project_health_metrics.arn
    launch_type         = "FARGATE"
    network_configuration {
      subnets          = var.private_subnet_ids
      security_groups  = [var.lambda_sg_id]
      assign_public_ip = false
    }
  }

  role_arn = aws_iam_role.event_bridge_role.arn
}

resource "aws_ecs_task_definition" "owasp_update_project_health_scores" {
  family                   = "${var.project_name}-${var.environment}-owasp-update-project-health-scores"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.update_project_health_scores_task_cpu
  memory                   = var.update_project_health_scores_task_memory
  execution_role_arn       = aws_iam_role.ecs_tasks_execution_role.arn
  tags                     = local.common_tags

  container_definitions = jsonencode([
    {
      name      = "backend"
      image     = aws_ecr_repository.main.repository_url
      command   = ["python", "manage.py", "owasp-update-project-health-scores"]
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.owasp_update_project_health_scores.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

resource "aws_cloudwatch_log_group" "owasp_update_project_health_scores" {
  name = "/ecs/${var.project_name}-${var.environment}-owasp-update-project-health-scores"
  tags = local.common_tags
}

resource "aws_cloudwatch_event_rule" "owasp_update_project_health_scores" {
  name                = "${var.project_name}-${var.environment}-owasp-update-project-health-scores-rule"
  description         = "Fires daily to trigger the owasp-update-project-health-scores task"
  schedule_expression = "cron(22 17 * * ? *)"
  tags                = local.common_tags
}

resource "aws_cloudwatch_event_target" "owasp_update_project_health_scores" {
  rule      = aws_cloudwatch_event_rule.owasp_update_project_health_scores.name
  target_id = "${var.project_name}-${var.environment}-owasp-update-project-health-scores-target"
  arn       = aws_ecs_cluster.main.arn

  ecs_target {
    task_definition_arn = aws_ecs_task_definition.owasp_update_project_health_scores.arn
    launch_type         = "FARGATE"
    network_configuration {
      subnets          = var.private_subnet_ids
      security_groups  = [var.lambda_sg_id]
      assign_public_ip = false
    }
  }

  role_arn = aws_iam_role.event_bridge_role.arn
}

# One time tasks
resource "aws_ecs_task_definition" "migrate" {
  family                   = "${var.project_name}-${var.environment}-migrate"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.migrate_task_cpu
  memory                   = var.migrate_task_memory
  execution_role_arn       = aws_iam_role.ecs_tasks_execution_role.arn
  tags                     = local.common_tags

  container_definitions = jsonencode([
    {
      name      = "backend"
      image     = "${aws_ecr_repository.main.repository_url}:latest"
      command   = ["python", "manage.py", "migrate"]
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.load_data.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
      environment = [
        {
          name  = "DJANGO_ALGOLIA_APPLICATION_ID"
          value = var.django_algolia_application_id
        },
        {
          name  = "DJANGO_ALGOLIA_WRITE_API_KEY"
          value = var.django_algolia_write_api_key
        },
        {
          name  = "DJANGO_ALLOWED_HOSTS"
          value = var.django_allowed_hosts
        },
        {
          name  = "DJANGO_AWS_ACCESS_KEY_ID"
          value = var.django_aws_access_key_id
        },
        {
          name  = "DJANGO_AWS_SECRET_ACCESS_KEY"
          value = var.django_aws_secret_access_key
        },
        {
          name  = "DJANGO_CONFIGURATION"
          value = var.django_configuration
        },
        {
          name  = "DJANGO_DB_HOST"
          value = var.django_db_host
        },
        {
          name  = "DJANGO_DB_NAME"
          value = var.django_db_name
        },
        {
          name  = "DJANGO_DB_USER"
          value = var.django_db_user
        },
        {
          name  = "DJANGO_DB_PORT"
          value = var.django_db_port
        },
        {
          name  = "DJANGO_DB_PASSWORD"
          value = var.django_db_password
        },
        {
          name  = "DJANGO_OPEN_AI_SECRET_KEY"
          value = var.django_open_ai_secret_key
        },
        {
          name  = "DJANGO_REDIS_HOST"
          value = var.django_redis_host
        },
        {
          name  = "DJANGO_REDIS_PASSWORD"
          value = var.django_redis_password
        },
        {
          name  = "DJANGO_SECRET_KEY"
          value = var.django_secret_key
        },
        {
          name  = "DJANGO_SENTRY_DSN"
          value = var.django_sentry_dsn
        },
        {
          name  = "DJANGO_SLACK_BOT_TOKEN"
          value = var.django_slack_bot_token
        },
        {
          name  = "DJANGO_SLACK_SIGNING_SECRET"
          value = var.django_slack_signing_secret
        }
      ]
    }
  ])
}

resource "aws_cloudwatch_log_group" "migrate" {
  name = "/ecs/${var.project_name}-${var.environment}-migrate"
  tags = local.common_tags
}

resource "aws_ecs_task_definition" "load_data" {
  family                   = "${var.project_name}-${var.environment}-load-data"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.load_data_task_cpu
  memory                   = var.load_data_task_memory
  execution_role_arn       = aws_iam_role.ecs_tasks_execution_role.arn
  tags                     = local.common_tags

  container_definitions = jsonencode([
    {
      name      = "backend"
      image     = "${aws_ecr_repository.main.repository_url}:latest"
      command   = ["python", "manage.py", "load_data"]
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.load_data.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
      environment = [
        {
          name  = "DJANGO_ALGOLIA_APPLICATION_ID"
          value = var.django_algolia_application_id
        },
        {
          name  = "DJANGO_ALGOLIA_WRITE_API_KEY"
          value = var.django_algolia_write_api_key
        },
        {
          name  = "DJANGO_ALLOWED_HOSTS"
          value = var.django_allowed_hosts
        },
        {
          name  = "DJANGO_AWS_ACCESS_KEY_ID"
          value = var.django_aws_access_key_id
        },
        {
          name  = "DJANGO_AWS_SECRET_ACCESS_KEY"
          value = var.django_aws_secret_access_key
        },
        {
          name  = "DJANGO_CONFIGURATION"
          value = var.django_configuration
        },
        {
          name  = "DJANGO_DB_HOST"
          value = var.django_db_host
        },
        {
          name  = "DJANGO_DB_NAME"
          value = var.django_db_name
        },
        {
          name  = "DJANGO_DB_USER"
          value = var.django_db_user
        },
        {
          name  = "DJANGO_DB_PORT"
          value = var.django_db_port
        },
        {
          name  = "DJANGO_DB_PASSWORD"
          value = var.django_db_password
        },
        {
          name  = "DJANGO_OPEN_AI_SECRET_KEY"
          value = var.django_open_ai_secret_key
        },
        {
          name  = "DJANGO_REDIS_HOST"
          value = var.django_redis_host
        },
        {
          name  = "DJANGO_REDIS_PASSWORD"
          value = var.django_redis_password
        },
        {
          name  = "DJANGO_SECRET_KEY"
          value = var.django_secret_key
        },
        {
          name  = "DJANGO_SENTRY_DSN"
          value = var.django_sentry_dsn
        },
        {
          name  = "DJANGO_SLACK_BOT_TOKEN"
          value = var.django_slack_bot_token
        },
        {
          name  = "DJANGO_SLACK_SIGNING_SECRET"
          value = var.django_slack_signing_secret
        }
      ]
    }
  ])
}

resource "aws_cloudwatch_log_group" "load_data" {
  name = "/ecs/${var.project_name}-${var.environment}-load-data"
  tags = local.common_tags
}

resource "aws_ecs_task_definition" "index_data" {
  family                   = "${var.project_name}-${var.environment}-index-data"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.index_data_task_cpu
  memory                   = var.index_data_task_memory
  execution_role_arn       = aws_iam_role.ecs_tasks_execution_role.arn
  tags                     = local.common_tags

  container_definitions = jsonencode([
    {
      name  = "backend"
      image = "${aws_ecr_repository.main.repository_url}:latest"
      command = [
        "/bin/sh",
        "-c",
        <<-EOT
        python manage.py algolia_reindex
        python manage.py algolia_update_replicas
        python manage.py algolia_update_synonyms
        EOT
      ]
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.load_data.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
      environment = [
        {
          name  = "DJANGO_ALGOLIA_APPLICATION_ID"
          value = var.django_algolia_application_id
        },
        {
          name  = "DJANGO_ALGOLIA_WRITE_API_KEY"
          value = var.django_algolia_write_api_key
        },
        {
          name  = "DJANGO_ALLOWED_HOSTS"
          value = var.django_allowed_hosts
        },
        {
          name  = "DJANGO_AWS_ACCESS_KEY_ID"
          value = var.django_aws_access_key_id
        },
        {
          name  = "DJANGO_AWS_SECRET_ACCESS_KEY"
          value = var.django_aws_secret_access_key
        },
        {
          name  = "DJANGO_CONFIGURATION"
          value = var.django_configuration
        },
        {
          name  = "DJANGO_DB_HOST"
          value = var.django_db_host
        },
        {
          name  = "DJANGO_DB_NAME"
          value = var.django_db_name
        },
        {
          name  = "DJANGO_DB_USER"
          value = var.django_db_user
        },
        {
          name  = "DJANGO_DB_PORT"
          value = var.django_db_port
        },
        {
          name  = "DJANGO_DB_PASSWORD"
          value = var.django_db_password
        },
        {
          name  = "DJANGO_OPEN_AI_SECRET_KEY"
          value = var.django_open_ai_secret_key
        },
        {
          name  = "DJANGO_REDIS_HOST"
          value = var.django_redis_host
        },
        {
          name  = "DJANGO_REDIS_PASSWORD"
          value = var.django_redis_password
        },
        {
          name  = "DJANGO_SECRET_KEY"
          value = var.django_secret_key
        },
        {
          name  = "DJANGO_SENTRY_DSN"
          value = var.django_sentry_dsn
        },
        {
          name  = "DJANGO_SLACK_BOT_TOKEN"
          value = var.django_slack_bot_token
        },
        {
          name  = "DJANGO_SLACK_SIGNING_SECRET"
          value = var.django_slack_signing_secret
        }
      ]
    }
  ])
}

resource "aws_cloudwatch_log_group" "index_data" {
  name = "/ecs/${var.project_name}-${var.environment}-index-data"
  tags = local.common_tags
}
