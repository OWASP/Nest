locals {
  grafana_enabled = var.grafana_image != null

  grafana_container_definition = {
    name      = "grafana"
    image     = var.grafana_image
    essential = true
    user      = "472:472"
    environment = [
      { name = "GF_AUTH_ANONYMOUS_ENABLED", value = "false" },
      { name = "GF_USERS_ALLOW_SIGN_UP", value = "false" },
      # Credentials will be wired separately; never bootstrap admin/admin.
      { name = "GF_SECURITY_DISABLE_INITIAL_ADMIN_CREATION", value = "true" },
      { name = "GF_DATABASE_WAL", value = "false" },
      { name = "GF_LOG_MODE", value = "console" },
      { name = "O11Y_METRICS_URL", value = "http://${aws_service_discovery_service.vm.name}.${aws_service_discovery_private_dns_namespace.vm.name}:${var.vm_port}" }
    ]
    portMappings = [{ containerPort = 3000, hostPort = 3000, protocol = "tcp" }]
    healthCheck = {
      command     = ["CMD-SHELL", "wget --spider -q http://127.0.0.1:3000/api/health || exit 1"]
      interval    = 30
      retries     = 3
      startPeriod = 60
      timeout     = 5
    }
    mountPoints = [{ containerPath = "/var/lib/grafana", sourceVolume = "grafana-data", readOnly = false }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/aws/ecs/${local.name_prefix}-grafana"
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }
}

resource "aws_cloudwatch_log_group" "grafana" {
  count             = local.grafana_enabled ? 1 : 0
  name              = "/aws/ecs/${local.name_prefix}-grafana"
  kms_key_id        = var.kms_key_arn
  retention_in_days = var.log_retention_in_days
  tags              = var.common_tags
}

resource "aws_iam_role_policy" "grafana_logs" {
  count = local.grafana_enabled ? 1 : 0
  name  = "grafana-logs"
  role  = aws_iam_role.grafana_execution.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["logs:CreateLogStream", "logs:PutLogEvents"]
      Resource = "${aws_cloudwatch_log_group.grafana[0].arn}:*"
    }]
  })
}

resource "aws_efs_access_point" "grafana" {
  count          = local.grafana_enabled ? 1 : 0
  file_system_id = aws_efs_file_system.vm.id
  posix_user {
    uid = 472
    gid = 472
  }
  root_directory {
    path = "/grafana"
    creation_info {
      owner_uid   = 472
      owner_gid   = 472
      permissions = "0700"
    }
  }
  tags = var.common_tags
}

resource "aws_security_group" "grafana" {
  count       = local.grafana_enabled ? 1 : 0
  name        = "${local.name_prefix}-grafana-sg"
  description = "Grafana task networking; ingress is added with the ALB integration"
  vpc_id      = var.vpc_id
  tags        = var.common_tags
}

resource "aws_security_group_rule" "grafana_https" {
  count             = local.grafana_enabled ? 1 : 0
  description       = "HTTPS for image pulls and CloudWatch Logs"
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.grafana[0].id
}

resource "aws_security_group_rule" "grafana_to_efs" {
  count                    = local.grafana_enabled ? 1 : 0
  description              = "Grafana persistent data access"
  type                     = "egress"
  from_port                = 2049
  to_port                  = 2049
  protocol                 = "tcp"
  security_group_id        = aws_security_group.grafana[0].id
  source_security_group_id = aws_security_group.efs.id
}

resource "aws_security_group_rule" "efs_from_grafana" {
  count                    = local.grafana_enabled ? 1 : 0
  description              = "NFS from Grafana"
  type                     = "ingress"
  from_port                = 2049
  to_port                  = 2049
  protocol                 = "tcp"
  security_group_id        = aws_security_group.efs.id
  source_security_group_id = aws_security_group.grafana[0].id
}

resource "aws_security_group_rule" "grafana_to_metrics" {
  count                    = local.grafana_enabled ? 1 : 0
  description              = "Grafana datasource queries"
  type                     = "egress"
  from_port                = var.vm_port
  to_port                  = var.vm_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.grafana[0].id
  source_security_group_id = aws_security_group.vm.id
}

resource "aws_security_group_rule" "metrics_from_grafana" {
  count                    = local.grafana_enabled ? 1 : 0
  description              = "Metrics queries from Grafana"
  type                     = "ingress"
  from_port                = var.vm_port
  to_port                  = var.vm_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.vm.id
  source_security_group_id = aws_security_group.grafana[0].id
}

resource "aws_ecs_task_definition" "grafana" {
  count                    = local.grafana_enabled ? 1 : 0
  family                   = "${local.name_prefix}-grafana"
  cpu                      = 256
  memory                   = 512
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.grafana_execution.arn
  container_definitions    = jsonencode([local.grafana_container_definition])
  tags                     = var.common_tags
  runtime_platform {
    cpu_architecture        = "ARM64"
    operating_system_family = "LINUX"
  }
  volume {
    name = "grafana-data"
    efs_volume_configuration {
      file_system_id     = aws_efs_file_system.vm.id
      transit_encryption = "ENABLED"
      authorization_config {
        access_point_id = aws_efs_access_point.grafana[0].id
      }
    }
  }
}

resource "aws_ecs_service" "grafana" {
  count                              = local.grafana_enabled ? 1 : 0
  name                               = "${local.name_prefix}-grafana"
  cluster                            = aws_ecs_cluster.vm.id
  task_definition                    = aws_ecs_task_definition.grafana[0].arn
  desired_count                      = var.grafana_desired_count
  deployment_maximum_percent         = 100
  deployment_minimum_healthy_percent = 0
  tags                               = var.common_tags
  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 1
  }
  network_configuration {
    assign_public_ip = false
    security_groups  = [aws_security_group.grafana[0].id]
    subnets          = var.subnet_ids
  }
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }
  depends_on = [
    aws_efs_mount_target.vm,
    aws_iam_role_policy_attachment.grafana_image_pull,
    aws_iam_role_policy.grafana_logs,
    aws_security_group_rule.grafana_https,
    aws_security_group_rule.grafana_to_efs,
    aws_security_group_rule.efs_from_grafana,
    aws_security_group_rule.grafana_to_metrics,
    aws_security_group_rule.metrics_from_grafana,
  ]
}
