terraform {
  required_version = "~> 1.15.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.58.0"
    }
  }
}

locals {
  name_prefix = "${var.project_name}-${var.environment}-observability"

  vm_container_definition = {
    command = [
      "-storageDataPath=/data",
      "-retentionPeriod=${var.vm_retention_period}",
      "-httpListenAddr=:${var.vm_port}",
    ]
    essential = true
    healthCheck = {
      command     = ["CMD-SHELL", "wget --spider -q http://localhost:${var.vm_port}/health || exit 1"]
      interval    = 30
      retries     = 3
      startPeriod = 30
      timeout     = 5
    }
    image = var.vm_image
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.vm.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
    mountPoints = [
      {
        containerPath = "/data"
        readOnly      = false
        sourceVolume  = "vm-data"
      }
    ]
    name = "victoriametrics"
    portMappings = [
      {
        containerPort = var.vm_port
        hostPort      = var.vm_port
        protocol      = "tcp"
      }
    ]
    user = "65532"
  }
}

resource "aws_security_group" "vm" {
  description = "Security group for the VictoriaMetrics task"
  name        = "${local.name_prefix}-vm-sg"
  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-vm-sg"
  })
  vpc_id = var.vpc_id
}

resource "aws_security_group_rule" "vm_ingest_from_apps" {
  count = length(var.app_security_group_ids)

  description              = "Allow metrics ingest and queries from application tasks"
  from_port                = var.vm_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.vm.id
  source_security_group_id = var.app_security_group_ids[count.index]
  to_port                  = var.vm_port
  type                     = "ingress"
}

resource "aws_security_group_rule" "vm_egress_https" {
  cidr_blocks       = ["0.0.0.0/0"]
  description       = "Allow HTTPS egress for container image pulls"
  from_port         = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.vm.id
  to_port           = 443
  type              = "egress"
}

resource "aws_security_group_rule" "vm_to_efs" {
  description              = "Allow NFS to the observability EFS"
  from_port                = 2049
  protocol                 = "tcp"
  security_group_id        = aws_security_group.vm.id
  source_security_group_id = aws_security_group.efs.id
  to_port                  = 2049
  type                     = "egress"
}

resource "aws_security_group" "efs" {
  description = "Security group for the observability EFS file system"
  name        = "${local.name_prefix}-efs-sg"
  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-efs-sg"
  })
  vpc_id = var.vpc_id
}

resource "aws_security_group_rule" "efs_from_vm" {
  description              = "Allow NFS from the VictoriaMetrics task"
  from_port                = 2049
  protocol                 = "tcp"
  security_group_id        = aws_security_group.efs.id
  source_security_group_id = aws_security_group.vm.id
  to_port                  = 2049
  type                     = "ingress"
}

resource "aws_efs_file_system" "vm" {
  encrypted  = true
  kms_key_id = var.kms_key_arn
  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-vm"
  })

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_efs_mount_target" "vm" {
  count = length(var.subnet_ids)

  file_system_id  = aws_efs_file_system.vm.id
  security_groups = [aws_security_group.efs.id]
  subnet_id       = var.subnet_ids[count.index]
}

resource "aws_efs_access_point" "vm" {
  file_system_id = aws_efs_file_system.vm.id

  posix_user {
    gid = 65532
    uid = 65532
  }

  root_directory {
    path = "/victoriametrics"

    creation_info {
      owner_gid   = 65532
      owner_uid   = 65532
      permissions = "0755"
    }
  }

  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-vm"
  })
}

resource "aws_cloudwatch_log_group" "vm" {
  kms_key_id        = var.kms_key_arn
  name              = "/aws/ecs/${local.name_prefix}"
  retention_in_days = var.log_retention_in_days
  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-logs"
  })
}

resource "aws_ecs_cluster" "vm" {
  name = "${local.name_prefix}-cluster"
  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-cluster"
  })

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_cluster_capacity_providers" "vm" {
  capacity_providers = ["FARGATE"]
  cluster_name       = aws_ecs_cluster.vm.name

  default_capacity_provider_strategy {
    base              = 0
    capacity_provider = "FARGATE"
    weight            = 1
  }
}

resource "aws_iam_role" "ecs_task_execution_role" {
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
  name = "${local.name_prefix}-execution-role"
  tags = var.common_tags
}

resource "aws_iam_policy" "ecs_task_execution_policy" {
  description = "Policy for the VictoriaMetrics ECS task execution - CloudWatch Logs access."
  name        = "${local.name_prefix}-execution-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "${aws_cloudwatch_log_group.vm.arn}:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy_attachment" {
  policy_arn = aws_iam_policy.ecs_task_execution_policy.arn
  role       = aws_iam_role.ecs_task_execution_role.name
}

resource "aws_ecs_task_definition" "vm" {
  container_definitions    = jsonencode([local.vm_container_definition])
  cpu                      = var.vm_cpu
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  family                   = local.name_prefix
  memory                   = var.vm_memory
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  runtime_platform {
    cpu_architecture        = "ARM64"
    operating_system_family = "LINUX"
  }
  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-task-def"
  })

  volume {
    name = "vm-data"

    efs_volume_configuration {
      file_system_id     = aws_efs_file_system.vm.id
      transit_encryption = "ENABLED"

      authorization_config {
        access_point_id = aws_efs_access_point.vm.id
      }
    }
  }
}

resource "aws_ecs_service" "vm" {
  cluster                            = aws_ecs_cluster.vm.id
  deployment_maximum_percent         = 100
  deployment_minimum_healthy_percent = 0
  desired_count                      = var.vm_desired_count
  name                               = "${local.name_prefix}-service"
  tags = merge(var.common_tags, {
    Name = "${local.name_prefix}-service"
  })
  task_definition = aws_ecs_task_definition.vm.arn

  capacity_provider_strategy {
    base              = 0
    capacity_provider = "FARGATE"
    weight            = 1
  }

  network_configuration {
    assign_public_ip = var.assign_public_ip
    security_groups  = [aws_security_group.vm.id]
    subnets          = var.subnet_ids
  }

  depends_on = [aws_efs_mount_target.vm]
}
