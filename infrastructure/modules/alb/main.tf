terraform {
  required_version = "1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.22.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.7.2"
    }
  }
}

locals {
  backend_paths = [
    "/a",
    "/a/*",
    "/api/*",
    "/csrf",
    "/csrf/*",
    "/graphql",
    "/graphql/*",
    "/idx",
    "/idx/*",
    "/integrations",
    "/integrations/*",
    "/sitemap",
    "/sitemap.xml",
    "/status",
    "/status/*",
  ]
  backend_path_chunks = chunklist(local.backend_paths, 5)
}

data "aws_elb_service_account" "main" {}

data "aws_lambda_function" "backend" {
  count         = var.lambda_function_name != null ? 1 : 0
  function_name = var.lambda_function_name
}

data "aws_iam_policy_document" "alb_logs" {
  statement {
    actions   = ["s3:PutObject"]
    effect    = "Allow"
    resources = ["${aws_s3_bucket.alb_logs.arn}/*"]
    sid       = "AllowALBLogDelivery"

    principals {
      identifiers = [data.aws_elb_service_account.main.arn]
      type        = "AWS"
    }
  }
}

resource "aws_acm_certificate" "main" {
  domain_name = var.domain_name
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-alb-cert"
  })
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_lambda_alias" "live" {
  count            = var.lambda_function_name != null ? 1 : 0
  description      = "Alias pointing to latest published version for SnapStart"
  function_name    = var.lambda_function_name
  function_version = data.aws_lambda_function.backend[0].version
  name             = "live"

  lifecycle {
    create_before_destroy = true
    ignore_changes        = [function_version]
  }
}

resource "aws_lambda_permission" "alb" {
  count         = var.lambda_function_name != null ? 1 : 0
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "elasticloadbalancing.amazonaws.com"
  qualifier     = aws_lambda_alias.live[0].name
  source_arn    = aws_lb_target_group.lambda[0].arn
  statement_id  = "AllowALBInvoke"
}

resource "aws_lb" "main" {
  depends_on                 = [aws_s3_bucket_policy.alb_logs]
  drop_invalid_header_fields = true
  enable_deletion_protection = false
  internal                   = false
  load_balancer_type         = "application"
  name                       = "${var.project_name}-${var.environment}-alb"
  security_groups            = [var.alb_sg_id]
  subnets                    = var.public_subnet_ids
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-alb"
  })

  access_logs {
    bucket  = aws_s3_bucket.alb_logs.id
    enabled = true
    prefix  = "alb"
  }
}

resource "aws_lb_listener" "http_redirect" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP" #NOSONAR
  tags              = var.common_tags

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener" "https" {
  certificate_arn   = aws_acm_certificate.main.arn
  load_balancer_arn = aws_lb.main.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  tags              = var.common_tags

  default_action {
    target_group_arn = aws_lb_target_group.frontend.arn
    type             = "forward"
  }
}

resource "aws_lb_listener_rule" "backend_https" {
  for_each     = var.lambda_function_name != null ? { for idx, chunk in local.backend_path_chunks : idx => chunk } : {}
  listener_arn = aws_lb_listener.https.arn
  priority     = 100 + each.key
  tags         = var.common_tags

  action {
    target_group_arn = aws_lb_target_group.lambda[0].arn
    type             = "forward"
  }

  condition {
    path_pattern {
      values = each.value
    }
  }
}

resource "aws_lb_target_group" "frontend" {
  deregistration_delay = 30
  name                 = "${var.project_name}-${var.environment}-frontend-tg"
  port                 = var.frontend_port
  protocol             = "HTTP"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-frontend-tg"
  })
  target_type = "ip"
  vpc_id      = var.vpc_id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200-299"
    path                = var.frontend_health_check_path
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 3
  }
}

resource "aws_lb_target_group" "lambda" {
  count       = var.lambda_function_name != null ? 1 : 0
  name        = "${var.project_name}-${var.environment}-lambda-tg"
  target_type = "lambda"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-lambda-tg"
  })
}

resource "aws_lb_target_group_attachment" "lambda" {
  count            = var.lambda_function_name != null ? 1 : 0
  depends_on       = [aws_lambda_permission.alb]
  target_group_arn = aws_lb_target_group.lambda[0].arn
  target_id        = aws_lambda_alias.live[0].arn
}

resource "aws_s3_bucket" "alb_logs" { # NOSONAR
  bucket = "${var.project_name}-${var.environment}-alb-logs-${random_id.suffix.hex}"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-alb-logs"
  })

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id

  rule {
    id     = "expire-logs"
    status = "Enabled"

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
    expiration {
      days = var.log_retention_days
    }
  }
}

resource "aws_s3_bucket_policy" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id
  policy = data.aws_iam_policy_document.alb_logs.json
}

resource "aws_s3_bucket_public_access_block" "alb_logs" {
  block_public_acls       = true
  block_public_policy     = true
  bucket                  = aws_s3_bucket.alb_logs.id
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "random_id" "suffix" {
  byte_length = 4
}
