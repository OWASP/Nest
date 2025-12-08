terraform {
  required_version = "1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.22.0"
    }
  }
}

resource "aws_lb" "main" {
  enable_deletion_protection = false
  internal                   = false
  load_balancer_type         = "application"
  name                       = "${var.project_name}-${var.environment}-frontend-alb"
  security_groups            = [var.alb_sg_id]
  subnets                    = var.public_subnet_ids
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-frontend-alb"
  })
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"
  tags              = var.common_tags

  default_action {
    target_group_arn = aws_lb_target_group.main.arn
    type             = "forward"
  }
}

resource "aws_lb_listener" "https" {
  certificate_arn   = var.acm_certificate_arn
  count             = var.enable_https ? 1 : 0
  load_balancer_arn = aws_lb.main.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  tags              = var.common_tags

  default_action {
    target_group_arn = aws_lb_target_group.main.arn
    type             = "forward"
  }
}

resource "aws_lb_target_group" "main" {
  deregistration_delay = 30
  name                 = "${var.project_name}-${var.environment}-frontend-tg"
  port                 = 3000
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
    path                = var.health_check_path
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 3
  }
}
