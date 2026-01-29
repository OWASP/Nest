variables {
  alb_sg_id                  = "sg-alb-12345"
  aws_region                 = "us-east-2"
  common_tags                = { Environment = "test", Project = "nest" }
  domain_name                = "nest.owasp.dev"
  environment                = "test"
  frontend_health_check_path = "/"
  frontend_port              = 3000
  lambda_function_name       = null
  log_retention_days         = 90
  project_name               = "nest"
  public_subnet_ids          = ["subnet-public-1", "subnet-public-2"]
  vpc_id                     = "vpc-12345678"
}

run "test_acm_certificate_domain_name" {
  command = plan

  assert {
    condition     = aws_acm_certificate.main.domain_name == var.domain_name
    error_message = "ACM certificate domain name must match the domain_name variable."
  }
}

run "test_acm_certificate_validation_method" {
  command = plan

  assert {
    condition     = aws_acm_certificate.main.validation_method == "DNS"
    error_message = "ACM certificate must use DNS validation method."
  }
}

run "test_acm_certificate_name_format" {
  command = plan

  assert {
    condition     = aws_acm_certificate.main.tags.Name == "${var.project_name}-${var.environment}-alb-cert"
    error_message = "ACM certificate name must follow format: {project}-{environment}-alb-cert."
  }
}

run "test_lambda_alias_not_created_when_null" {
  command = plan

  variables {
    lambda_function_name = null
  }
  assert {
    condition     = length(aws_lambda_alias.live) == 0
    error_message = "Lambda alias should not be created when lambda_function_name is null."
  }
}

run "test_lambda_alias_name" {
  command = plan

  override_data {
      target = data.aws_lambda_function.backend[0]
      values = {
        version = "1"
      }
  }
  variables {
    lambda_function_name = "test-function"
  }
  assert {
    condition     = aws_lambda_alias.live[0].name == "live"
    error_message = "Lambda alias name must be 'live'."
  }
}

run "test_lambda_permission_not_created_when_null" {
  command = plan

  variables {
    lambda_function_name = null
  }
  assert {
    condition     = length(aws_lambda_permission.alb) == 0
    error_message = "Lambda permission should not be created when lambda_function_name is null."
  }
}

run "test_lambda_permission_action" {
  command = plan

  override_data {
      target = data.aws_lambda_function.backend[0]
      values = {
        version = "1"
      }
  }
  variables {
    lambda_function_name = "test-function"
  }
  assert {
    condition     = aws_lambda_permission.alb[0].action == "lambda:InvokeFunction"
    error_message = "Lambda permission action must be 'lambda:InvokeFunction'."
  }
}

run "test_lambda_permission_principal" {
  command = plan

  override_data {
      target = data.aws_lambda_function.backend[0]
      values = {
        version = "1"
      }
  }
  variables {
    lambda_function_name = "test-function"
  }
  assert {
    condition     = aws_lambda_permission.alb[0].principal == "elasticloadbalancing.amazonaws.com"
    error_message = "Lambda permission principal must be 'elasticloadbalancing.amazonaws.com'."
  }
}

run "test_alb_name_format" {
  command = plan
  assert {
    condition     = aws_lb.main.name == "${var.project_name}-${var.environment}-alb"
    error_message = "ALB name must follow format: {project}-{environment}-alb."
  }
}

run "test_alb_drops_invalid_headers" {
  command = plan
  assert {
    condition     = aws_lb.main.drop_invalid_header_fields == true
    error_message = "ALB must drop invalid header fields."
  }
}

run "test_alb_access_logs_enabled" {
  command = plan
  assert {
    condition     = aws_lb.main.access_logs[0].enabled == true
    error_message = "ALB access logs must be enabled."
  }
}

run "test_alb_access_logs_prefix" {
  command = plan
  assert {
    condition     = aws_lb.main.access_logs[0].prefix == "alb"
    error_message = "ALB access logs prefix must be 'alb'."
  }
}

run "test_http_listener_port" {
  command = plan
  assert {
    condition     = aws_lb_listener.http_redirect.port == 80
    error_message = "HTTP listener port must be 80."
  }
}

run "test_http_listener_protocol" {
  command = plan
  assert {
    condition     = aws_lb_listener.http_redirect.protocol == "HTTP"
    error_message = "HTTP listener protocol must be 'HTTP'."
  }
}

run "test_http_redirect_port" {
  command = plan
  assert {
    condition     = aws_lb_listener.http_redirect.default_action[0].redirect[0].port == "443"
    error_message = "HTTP listener must redirect to port 443."
  }
}

run "test_http_redirect_protocol" {
  command = plan
  assert {
    condition     = aws_lb_listener.http_redirect.default_action[0].redirect[0].protocol == "HTTPS"
    error_message = "HTTP listener must redirect to HTTPS."
  }
}

run "test_http_redirect_status_code" {
  command = plan
  assert {
    condition     = aws_lb_listener.http_redirect.default_action[0].redirect[0].status_code == "HTTP_301"
    error_message = "HTTP listener redirect must use HTTP_301 status code."
  }
}

run "test_https_listener_port" {
  command = plan
  assert {
    condition     = aws_lb_listener.https.port == 443
    error_message = "HTTPS listener port must be 443."
  }
}

run "test_https_listener_protocol" {
  command = plan
  assert {
    condition     = aws_lb_listener.https.protocol == "HTTPS"
    error_message = "HTTPS listener protocol must be 'HTTPS'."
  }
}

run "test_https_listener_ssl_policy" {
  command = plan
  assert {
    condition     = aws_lb_listener.https.ssl_policy == "ELBSecurityPolicy-TLS13-1-2-2021-06"
    error_message = "HTTPS listener must use TLS 1.3 security policy."
  }
}

run "test_backend_listener_rules_not_created_when_null" {
  command = plan
  variables {
    lambda_function_name = null
  }
  assert {
    condition     = length(aws_lb_listener_rule.backend_https) == 0
    error_message = "Backend listener rules should not be created when lambda_function_name is null."
  }
}

run "test_frontend_target_group_name_format" {
  command = plan
  assert {
    condition     = aws_lb_target_group.frontend.name == "${var.project_name}-${var.environment}-frontend-tg"
    error_message = "Frontend target group name must follow format: {project}-{environment}-frontend-tg."
  }
}

run "test_frontend_target_group_port" {
  command = plan
  assert {
    condition     = aws_lb_target_group.frontend.port == var.frontend_port
    error_message = "Frontend target group port must match the frontend_port variable."
  }
}

run "test_frontend_target_group_protocol" {
  command = plan
  assert {
    condition     = aws_lb_target_group.frontend.protocol == "HTTP"
    error_message = "Frontend target group protocol must be 'HTTP'."
  }
}

run "test_frontend_target_group_type" {
  command = plan
  assert {
    condition     = aws_lb_target_group.frontend.target_type == "ip"
    error_message = "Frontend target group target type must be 'ip'."
  }
}

run "test_frontend_target_group_deregistration_delay" {
  command = plan
  assert {
    condition     = aws_lb_target_group.frontend.deregistration_delay == "30"
    error_message = "Frontend target group deregistration delay must be 30 seconds."
  }
}

run "test_frontend_health_check_enabled" {
  command = plan
  assert {
    condition     = aws_lb_target_group.frontend.health_check[0].enabled == true
    error_message = "Frontend health check must be enabled."
  }
}

run "test_frontend_health_check_path" {
  command = plan
  assert {
    condition     = aws_lb_target_group.frontend.health_check[0].path == var.frontend_health_check_path
    error_message = "Frontend health check path must match the variable."
  }
}

run "test_frontend_health_check_healthy_threshold" {
  command = plan
  assert {
    condition     = aws_lb_target_group.frontend.health_check[0].healthy_threshold == 2
    error_message = "Frontend health check healthy threshold must be 2."
  }
}

run "test_frontend_health_check_unhealthy_threshold" {
  command = plan
  assert {
    condition     = aws_lb_target_group.frontend.health_check[0].unhealthy_threshold == 3
    error_message = "Frontend health check unhealthy threshold must be 3."
  }
}

run "test_frontend_health_check_timeout" {
  command = plan
  assert {
    condition     = aws_lb_target_group.frontend.health_check[0].timeout == 5
    error_message = "Frontend health check timeout must be 5 seconds."
  }
}

run "test_frontend_health_check_matcher" {
  command = plan
  assert {
    condition     = aws_lb_target_group.frontend.health_check[0].matcher == "200-299"
    error_message = "Frontend health check matcher must be '200-299'."
  }
}

run "test_lambda_target_group_not_created_when_null" {
  command = plan
  variables {
    lambda_function_name = null
  }
  assert {
    condition     = length(aws_lb_target_group.lambda) == 0
    error_message = "Lambda target group should not be created when lambda_function_name is null."
  }
}

run "test_lambda_target_group_name_format" {
  command = plan

  override_data {
      target = data.aws_lambda_function.backend[0]
      values = {
        version = "1"
      }
  }
  variables {
    lambda_function_name = "test-function"
  }
  assert {
    condition     = aws_lb_target_group.lambda[0].name == "${var.project_name}-${var.environment}-lambda-tg"
    error_message = "Lambda target group name must follow format: {project}-{environment}-lambda-tg."
  }
}

run "test_lambda_target_group_type" {
  command = plan

  override_data {
      target = data.aws_lambda_function.backend[0]
      values = {
        version = "1"
      }
  }
  variables {
    lambda_function_name = "test-function"
  }
  assert {
    condition     = aws_lb_target_group.lambda[0].target_type == "lambda"
    error_message = "Lambda target group target type must be 'lambda'."
  }
}

run "test_lambda_target_group_attachment_not_created_when_null" {
  command = plan
  variables {
    lambda_function_name = null
  }
  assert {
    condition     = length(aws_lb_target_group_attachment.lambda) == 0
    error_message = "Lambda target group attachment should not be created when lambda_function_name is null."
  }
}

run "test_s3_bucket_lifecycle_expiration" {
  command = plan
  assert {
    condition     = aws_s3_bucket_lifecycle_configuration.alb_logs.rule[0].expiration[0].days == var.log_retention_days
    error_message = "S3 lifecycle must expire logs after log_retention_days."
  }
}

run "test_s3_bucket_lifecycle_multipart_abort" {
  command = plan
  assert {
    condition     = aws_s3_bucket_lifecycle_configuration.alb_logs.rule[0].abort_incomplete_multipart_upload[0].days_after_initiation == 7
    error_message = "S3 lifecycle must abort incomplete multipart uploads after 7 days."
  }
}

run "test_s3_public_access_block_all_blocked" {
  command = plan
  assert {
    condition = alltrue([
      aws_s3_bucket_public_access_block.alb_logs.block_public_acls,
      aws_s3_bucket_public_access_block.alb_logs.block_public_policy,
      aws_s3_bucket_public_access_block.alb_logs.ignore_public_acls,
      aws_s3_bucket_public_access_block.alb_logs.restrict_public_buckets
    ])
    error_message = "S3 bucket must block all public access."
  }
}

run "test_s3_versioning_enabled" {
  command = plan
  assert {
    condition     = aws_s3_bucket_versioning.alb_logs.versioning_configuration[0].status == "Enabled"
    error_message = "S3 bucket versioning must be enabled."
  }
}
