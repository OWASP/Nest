terraform {
  required_version = "~> 1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.36.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.8.0"
    }
  }
}

locals {
  backend_paths = [
    "/a",
    "/a/*",
    "/api/v0",
    "/api/v0/*",
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
  content_security_policy = join("; ", [
    "base-uri 'self'",
    "connect-src 'self' https://github-contributions-api.jogruber.de https://*.google-analytics.com https://*.i.posthog.com https://*.sentry.io https://*.tile.openstreetmap.org",
    "default-src 'self'",
    "font-src 'self' https://cdn.jsdelivr.net",
    "form-action 'self'",
    "frame-ancestors 'none'",
    "frame-src 'self'",
    "img-src 'self' data: https://authjs.dev https://avatars.githubusercontent.com https://*.tile.openstreetmap.org https://nest-staging-static-24d01951.s3.amazonaws.com https://owasp-nest-production.s3.amazonaws.com https://owasp-nest.s3.amazonaws.com https://owasp.org https://raw.githubusercontent.com",
    "object-src 'none'",
    "script-src 'self' 'unsafe-inline' https://*.i.posthog.com https://*.tile.openstreetmap.org https://nest-staging-static-24d01951.s3.amazonaws.com https://owasp-nest-production.s3.amazonaws.com https://owasp-nest.s3.amazonaws.com https://www.googletagmanager.com",
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://nest-staging-static-24d01951.s3.amazonaws.com https://owasp-nest-production.s3.amazonaws.com https://owasp-nest.s3.amazonaws.com",
  ])
}

data "aws_elb_service_account" "main" {}

resource "random_id" "suffix" {
  byte_length = 4
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

resource "aws_acm_certificate_validation" "main" {
  certificate_arn = aws_acm_certificate.main.arn

  validation_record_fqdns = [
    for dvo in aws_acm_certificate.main.domain_validation_options : dvo.resource_record_name
  ]
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
  certificate_arn                                              = aws_acm_certificate_validation.main.certificate_arn
  load_balancer_arn                                            = aws_lb.main.arn
  port                                                         = 443
  protocol                                                     = "HTTPS"
  routing_http_response_content_security_policy_header_value   = local.content_security_policy
  routing_http_response_strict_transport_security_header_value = "max-age=31536000; includeSubDomains; preload"
  routing_http_response_x_content_type_options_header_value    = "nosniff"
  routing_http_response_x_frame_options_header_value           = "DENY"
  ssl_policy                                                   = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  tags                                                         = var.common_tags

  default_action {
    target_group_arn = aws_lb_target_group.frontend.arn
    type             = "forward"
  }
}

resource "aws_lb_listener_rule" "backend_https" {
  for_each     = { for idx, chunk in local.backend_path_chunks : idx => chunk }
  listener_arn = aws_lb_listener.https.arn
  priority     = 100 + tonumber(each.key)
  tags         = var.common_tags

  action {
    target_group_arn = aws_lb_target_group.backend.arn
    type             = "forward"
  }
  condition {
    path_pattern {
      values = each.value
    }
  }
}

resource "aws_lb_target_group" "backend" {
  deregistration_delay = 30
  name                 = "${var.project_name}-${var.environment}-backend-tg"
  port                 = var.backend_port
  protocol             = "HTTP"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-backend-tg"
  })
  target_type = "ip"
  vpc_id      = var.vpc_id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200-299"
    path                = var.backend_health_check_path
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 3
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
    noncurrent_version_expiration {
      noncurrent_days = var.log_retention_days
    }
  }
}

resource "aws_s3_bucket_policy" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "AllowALBLogDelivery"
      Effect = "Allow"
      Principal = {
        AWS = data.aws_elb_service_account.main.arn
      }
      Action   = "s3:PutObject"
      Resource = "${aws_s3_bucket.alb_logs.arn}/*"
    }]
  })
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
