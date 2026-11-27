mock_provider "aws" {}

variables {
  common_tags  = { Environment = "test", Project = "nest" }
  db_port      = 5432
  environment  = "test"
  project_name = "nest"
  redis_port   = 6379
  vpc_id       = "vpc-12345678"
}

run "test_alb_security_group_name_format" {
  command = plan

  assert {
    condition     = aws_security_group.alb.name == "${var.project_name}-${var.environment}-alb-sg"
    error_message = "ALB security group name must follow format: {project}-{environment}-alb-sg."
  }
}

run "test_alb_http_rule_port" {
  command = plan

  assert {
    condition     = aws_security_group_rule.alb_http.from_port == 80
    error_message = "ALB HTTP rule must allow from_port 80."
  }
  assert {
    condition     = aws_security_group_rule.alb_http.to_port == 80
    error_message = "ALB HTTP rule must allow to_port 80."
  }
}

run "test_alb_http_rule_type" {
  command = plan

  assert {
    condition     = aws_security_group_rule.alb_http.type == "ingress"
    error_message = "ALB HTTP rule must be of type ingress."
  }
}

run "test_alb_https_rule_port" {
  command = plan

  assert {
    condition     = aws_security_group_rule.alb_https.from_port == 443
    error_message = "ALB HTTPS rule must allow from_port 443."
  }
  assert {
    condition     = aws_security_group_rule.alb_https.to_port == 443
    error_message = "ALB HTTPS rule must allow to_port 443."
  }
}

run "test_alb_https_rule_type" {
  command = plan

  assert {
    condition     = aws_security_group_rule.alb_https.type == "ingress"
    error_message = "ALB HTTPS rule must be of type ingress."
  }
}

run "test_alb_to_backend_rule_port" {
  command = plan

  assert {
    condition     = aws_security_group_rule.alb_to_backend.from_port == 8000
    error_message = "ALB to Backend rule must allow from_port 8000."
  }
  assert {
    condition     = aws_security_group_rule.alb_to_backend.to_port == 8000
    error_message = "ALB to Backend rule must allow to_port 8000."
  }
}

run "test_alb_to_backend_rule_type" {
  command = plan

  assert {
    condition     = aws_security_group_rule.alb_to_backend.type == "egress"
    error_message = "ALB to Backend rule must be of type egress."
  }
}

run "test_alb_to_frontend_rule_port" {
  command = plan

  assert {
    condition     = aws_security_group_rule.alb_to_frontend.from_port == 3000
    error_message = "ALB to Frontend rule must allow from_port 3000."
  }
  assert {
    condition     = aws_security_group_rule.alb_to_frontend.to_port == 3000
    error_message = "ALB to Frontend rule must allow to_port 3000."
  }
}

run "test_alb_to_frontend_rule_type" {
  command = plan

  assert {
    condition     = aws_security_group_rule.alb_to_frontend.type == "egress"
    error_message = "ALB to Frontend rule must be of type egress."
  }
}

run "test_backend_security_group_name_format" {
  command = plan
  assert {
    condition     = aws_security_group.backend.name == "${var.project_name}-${var.environment}-backend-sg"
    error_message = "Backend security group name must follow format: {project}-{environment}-backend-sg."
  }
}

run "test_backend_from_alb_rule_port" {
  command = plan
  assert {
    condition     = aws_security_group_rule.backend_from_alb.from_port == 8000
    error_message = "Backend ingress from ALB must allow from_port 8000."
  }
  assert {
    condition     = aws_security_group_rule.backend_from_alb.to_port == 8000
    error_message = "Backend ingress from ALB must allow to_port 8000."
  }
}

run "test_backend_from_alb_rule_type" {
  command = plan
  assert {
    condition     = aws_security_group_rule.backend_from_alb.type == "ingress"
    error_message = "Backend ingress from ALB must be of type ingress."
  }
}

run "test_backend_egress_https_rule_port" {
  command = plan
  assert {
    condition     = aws_security_group_rule.backend_egress_https.from_port == 443
    error_message = "Backend HTTPS egress rule must allow from_port 443."
  }
  assert {
    condition     = aws_security_group_rule.backend_egress_https.to_port == 443
    error_message = "Backend HTTPS egress rule must allow to_port 443."
  }
}

run "test_backend_egress_https_rule_type" {
  command = plan
  assert {
    condition     = aws_security_group_rule.backend_egress_https.type == "egress"
    error_message = "Backend HTTPS egress rule must be of type egress."
  }
  assert {
    condition     = aws_security_group_rule.backend_egress_https.protocol == "tcp"
    error_message = "Backend HTTPS egress rule must use protocol tcp."
  }
}

run "test_backend_to_rds_rule_port" {
  command = plan
  variables {
    enable_rds_proxy = false
  }
  assert {
    condition     = aws_security_group_rule.backend_to_rds[0].from_port == var.db_port
    error_message = "Backend to RDS egress rule must allow database port."
  }
  assert {
    condition     = aws_security_group_rule.backend_to_rds[0].to_port == var.db_port
    error_message = "Backend to RDS egress rule must allow database port."
  }
}

run "test_backend_to_rds_rule_type" {
  command = plan
  variables {
    enable_rds_proxy = false
  }
  assert {
    condition     = aws_security_group_rule.backend_to_rds[0].type == "egress"
    error_message = "Backend to RDS rule must be of type egress."
  }
}

run "test_backend_to_rds_proxy_rule_port" {
  command = plan
  variables {
    enable_rds_proxy = true
  }
  assert {
    condition     = aws_security_group_rule.backend_to_rds_proxy[0].from_port == var.db_port
    error_message = "Backend to RDS Proxy egress rule must allow database port."
  }
  assert {
    condition     = aws_security_group_rule.backend_to_rds_proxy[0].to_port == var.db_port
    error_message = "Backend to RDS Proxy egress rule must allow database port."
  }
}

run "test_backend_to_rds_proxy_rule_type" {
  command = plan
  variables {
    enable_rds_proxy = true
  }
  assert {
    condition     = aws_security_group_rule.backend_to_rds_proxy[0].type == "egress"
    error_message = "Backend to RDS Proxy rule must be of type egress."
  }
}

run "test_backend_to_redis_rule_port" {
  command = plan
  assert {
    condition     = aws_security_group_rule.backend_to_redis.from_port == var.redis_port
    error_message = "Backend to Redis egress rule must allow redis port."
  }
  assert {
    condition     = aws_security_group_rule.backend_to_redis.to_port == var.redis_port
    error_message = "Backend to Redis egress rule must allow redis port."
  }
}

run "test_backend_to_redis_rule_type" {
  command = plan
  assert {
    condition     = aws_security_group_rule.backend_to_redis.type == "egress"
    error_message = "Backend to Redis rule must be of type egress."
  }
}

run "test_tasks_security_group_name_format" {
  command = plan

  assert {
    condition     = aws_security_group.tasks.name == "${var.project_name}-${var.environment}-tasks-sg"
    error_message = "Tasks security group name must follow format: {project}-{environment}-tasks-sg."
  }
}

run "test_task_egress_https_rule_port" {
  command = plan
  assert {
    condition     = aws_security_group_rule.task_egress_https.from_port == 443
    error_message = "Task HTTPS egress rule must allow from_port 443."
  }
  assert {
    condition     = aws_security_group_rule.task_egress_https.to_port == 443
    error_message = "Task HTTPS egress rule must allow to_port 443."
  }
}

run "test_task_egress_https_rule_type" {
  command = plan
  assert {
    condition     = aws_security_group_rule.task_egress_https.type == "egress"
    error_message = "Task HTTPS egress rule must be of type egress."
  }
  assert {
    condition     = aws_security_group_rule.task_egress_https.protocol == "tcp"
    error_message = "Task HTTPS egress rule must use protocol tcp."
  }
}

run "test_task_to_rds_rule_port" {
  command = plan
  variables {
    enable_rds_proxy = false
  }
  assert {
    condition     = aws_security_group_rule.task_to_rds[0].from_port == var.db_port
    error_message = "Task to RDS egress rule must allow database port."
  }
  assert {
    condition     = aws_security_group_rule.task_to_rds[0].to_port == var.db_port
    error_message = "Task to RDS egress rule must allow database port."
  }
}

run "test_task_to_rds_rule_type" {
  command = plan
  variables {
    enable_rds_proxy = false
  }
  assert {
    condition     = aws_security_group_rule.task_to_rds[0].type == "egress"
    error_message = "Task to RDS rule must be of type egress."
  }
}

run "test_task_to_rds_proxy_rule_port" {
  command = plan
  variables {
    enable_rds_proxy = true
  }
  assert {
    condition     = aws_security_group_rule.task_to_rds_proxy[0].from_port == var.db_port
    error_message = "Task to RDS Proxy egress rule must allow database port."
  }
  assert {
    condition     = aws_security_group_rule.task_to_rds_proxy[0].to_port == var.db_port
    error_message = "Task to RDS Proxy egress rule must allow database port."
  }
}

run "test_task_to_rds_proxy_rule_type" {
  command = plan
  variables {
    enable_rds_proxy = true
  }
  assert {
    condition     = aws_security_group_rule.task_to_rds_proxy[0].type == "egress"
    error_message = "Task to RDS Proxy rule must be of type egress."
  }
}

run "test_task_to_redis_rule_port" {
  command = plan
  assert {
    condition     = aws_security_group_rule.task_to_redis.from_port == var.redis_port
    error_message = "Task to Redis egress rule must allow redis port."
  }
  assert {
    condition     = aws_security_group_rule.task_to_redis.to_port == var.redis_port
    error_message = "Task to Redis egress rule must allow redis port."
  }
}

run "test_task_to_redis_rule_type" {
  command = plan
  assert {
    condition     = aws_security_group_rule.task_to_redis.type == "egress"
    error_message = "Task to Redis rule must be of type egress."
  }
}

run "test_frontend_security_group_name_format" {
  command = plan
  assert {
    condition     = aws_security_group.frontend.name == "${var.project_name}-${var.environment}-frontend-sg"
    error_message = "Frontend security group name must follow format: {project}-{environment}-frontend-sg."
  }
}

run "test_frontend_from_alb_rule_port" {
  command = plan
  assert {
    condition     = aws_security_group_rule.frontend_from_alb.from_port == 3000
    error_message = "Frontend ingress from ALB must allow from_port 3000."
  }
  assert {
    condition     = aws_security_group_rule.frontend_from_alb.to_port == 3000
    error_message = "Frontend ingress from ALB must allow to_port 3000."
  }
}

run "test_frontend_from_alb_rule_type" {
  command = plan
  assert {
    condition     = aws_security_group_rule.frontend_from_alb.type == "ingress"
    error_message = "Frontend ingress from ALB must be of type ingress."
  }
}

run "test_frontend_https_rule_port" {
  command = plan
  assert {
    condition     = aws_security_group_rule.frontend_https.from_port == 443
    error_message = "Frontend HTTPS egress rule must allow from_port 443."
  }
  assert {
    condition     = aws_security_group_rule.frontend_https.to_port == 443
    error_message = "Frontend HTTPS egress rule must allow to_port 443."
  }
}

run "test_frontend_https_rule_type" {
  command = plan
  assert {
    condition     = aws_security_group_rule.frontend_https.type == "egress"
    error_message = "Frontend HTTPS egress rule must be of type egress."
  }
}

run "test_rds_security_group_name_format" {
  command = plan
  assert {
    condition     = aws_security_group.rds.name == "${var.project_name}-${var.environment}-rds-sg"
    error_message = "RDS security group name must follow format: {project}-{environment}-rds-sg."
  }
}

run "test_rds_proxy_security_group_name_format" {
  command = plan
  variables {
    enable_rds_proxy = true
  }
  assert {
    condition     = aws_security_group.rds_proxy[0].name == "${var.project_name}-${var.environment}-rds-proxy-sg"
    error_message = "RDS Proxy security group name must follow format: {project}-{environment}-rds-proxy-sg."
  }
}

run "test_rds_from_backend_rule_port" {
  command = plan
  variables {
    enable_rds_proxy = false
  }
  assert {
    condition     = aws_security_group_rule.rds_from_backend[0].from_port == var.db_port
    error_message = "RDS ingress from backend must allow database port."
  }
  assert {
    condition     = aws_security_group_rule.rds_from_backend[0].to_port == var.db_port
    error_message = "RDS ingress from backend must allow database port."
  }
}

run "test_rds_from_backend_rule_type" {
  command = plan
  variables {
    enable_rds_proxy = false
  }
  assert {
    condition     = aws_security_group_rule.rds_from_backend[0].type == "ingress"
    error_message = "RDS ingress from backend must be of type ingress."
  }
}

run "test_rds_from_task_rule_port" {
  command = plan
  variables {
    enable_rds_proxy = false
  }
  assert {
    condition     = aws_security_group_rule.rds_from_task[0].from_port == var.db_port
    error_message = "RDS ingress from ECS task must allow database port."
  }
  assert {
    condition     = aws_security_group_rule.rds_from_task[0].to_port == var.db_port
    error_message = "RDS ingress from ECS task must allow database port."
  }
}

run "test_rds_from_task_rule_type" {
  command = plan
  variables {
    enable_rds_proxy = false
  }
  assert {
    condition     = aws_security_group_rule.rds_from_task[0].type == "ingress"
    error_message = "RDS ingress from ECS task must be of type ingress."
  }
}

run "test_rds_from_proxy_rule_port" {
  command = plan
  variables {
    enable_rds_proxy = true
  }
  assert {
    condition     = aws_security_group_rule.rds_from_proxy[0].from_port == var.db_port
    error_message = "RDS to RDS Proxy ingress rule must allow database port."
  }
  assert {
    condition     = aws_security_group_rule.rds_from_proxy[0].to_port == var.db_port
    error_message = "RDS to RDS Proxy ingress rule must allow database port."
  }
}

run "test_rds_from_proxy_rule_type" {
  command = plan
  variables {
    enable_rds_proxy = true
  }
  assert {
    condition     = aws_security_group_rule.rds_from_proxy[0].type == "ingress"
    error_message = "RDS Proxy to RDS rule must be of type ingress."
  }
}

run "test_proxy_to_rds_rule_port" {
  command = plan
  variables {
    enable_rds_proxy = true
  }
  assert {
    condition     = aws_security_group_rule.rds_proxy_to_rds[0].from_port == var.db_port
    error_message = "RDS Proxy to RDS egress rule must allow database port."
  }
  assert {
    condition     = aws_security_group_rule.rds_proxy_to_rds[0].to_port == var.db_port
    error_message = "RDS Proxy to RDS egress rule must allow database port."
  }
}

run "test_proxy_to_rds_rule_type" {
  command = plan
  variables {
    enable_rds_proxy = true
  }
  assert {
    condition     = aws_security_group_rule.rds_proxy_to_rds[0].type == "egress"
    error_message = "RDS Proxy to RDS rule must be of type egress."
  }
}

run "test_rds_proxy_from_backend_rule_port" {
  command = plan
  variables {
    enable_rds_proxy = true
  }
  assert {
    condition     = aws_security_group_rule.rds_proxy_from_backend[0].from_port == var.db_port
    error_message = "RDS Proxy ingress from backend must allow database port."
  }
  assert {
    condition     = aws_security_group_rule.rds_proxy_from_backend[0].to_port == var.db_port
    error_message = "RDS Proxy ingress from backend must allow database port."
  }
}

run "test_rds_proxy_from_backend_rule_type" {
  command = plan
  variables {
    enable_rds_proxy = true
  }
  assert {
    condition     = aws_security_group_rule.rds_proxy_from_backend[0].type == "ingress"
    error_message = "RDS Proxy ingress from backend must be of type ingress."
  }
}

run "test_rds_proxy_from_task_rule_port" {
  command = plan
  variables {
    enable_rds_proxy = true
  }
  assert {
    condition     = aws_security_group_rule.rds_proxy_from_task[0].from_port == var.db_port
    error_message = "RDS Proxy ingress from ECS task must allow database port."
  }
  assert {
    condition     = aws_security_group_rule.rds_proxy_from_task[0].to_port == var.db_port
    error_message = "RDS Proxy ingress from ECS task must allow database port."
  }
}

run "test_rds_proxy_from_task_rule_type" {
  command = plan
  variables {
    enable_rds_proxy = true
  }
  assert {
    condition     = aws_security_group_rule.rds_proxy_from_task[0].type == "ingress"
    error_message = "RDS Proxy ingress from ECS task must be of type ingress."
  }
}

run "test_redis_security_group_name_format" {
  command = plan
  assert {
    condition     = aws_security_group.redis.name == "${var.project_name}-${var.environment}-redis-sg"
    error_message = "Redis security group name must follow format: {project}-{environment}-redis-sg."
  }
}

run "test_redis_from_backend_rule_port" {
  command = plan
  assert {
    condition     = aws_security_group_rule.redis_from_backend.from_port == var.redis_port
    error_message = "Redis ingress from backend must allow redis port."
  }
  assert {
    condition     = aws_security_group_rule.redis_from_backend.to_port == var.redis_port
    error_message = "Redis ingress from backend must allow redis port."
  }
}

run "test_redis_from_backend_rule_type" {
  command = plan
  assert {
    condition     = aws_security_group_rule.redis_from_backend.type == "ingress"
    error_message = "Redis ingress from backend must be of type ingress."
  }
}

run "test_redis_from_task_rule_port" {
  command = plan
  assert {
    condition     = aws_security_group_rule.redis_from_task.from_port == var.redis_port
    error_message = "Redis ingress from ECS task must allow redis port."
  }
  assert {
    condition     = aws_security_group_rule.redis_from_task.to_port == var.redis_port
    error_message = "Redis ingress from ECS task must allow redis port."
  }
}

run "test_redis_from_task_rule_type" {
  command = plan
  assert {
    condition     = aws_security_group_rule.redis_from_task.type == "ingress"
    error_message = "Redis ingress from ECS task must be of type ingress."
  }
}

run "test_backend_to_vpc_endpoints_rule_port" {
  command = plan
  variables {
    enable_vpc_endpoint_rules = true
    vpc_endpoint_sg_id        = "sg-endpoint123"
  }
  assert {
    condition     = aws_security_group_rule.backend_to_vpc_endpoints[0].from_port == 443
    error_message = "Backend to VPC endpoints rule must use port 443."
  }
  assert {
    condition     = aws_security_group_rule.backend_to_vpc_endpoints[0].to_port == 443
    error_message = "Backend to VPC endpoints rule must use port 443."
  }
}

run "test_backend_to_vpc_endpoints_rule_type" {
  command = plan
  variables {
    enable_vpc_endpoint_rules = true
    vpc_endpoint_sg_id        = "sg-endpoint123"
  }
  assert {
    condition     = aws_security_group_rule.backend_to_vpc_endpoints[0].type == "egress"
    error_message = "Backend to VPC endpoints rule must be of type egress."
  }
}

run "test_task_to_vpc_endpoints_rule_port" {
  command = plan
  variables {
    enable_vpc_endpoint_rules = true
    vpc_endpoint_sg_id        = "sg-endpoint123"
  }
  assert {
    condition     = aws_security_group_rule.task_to_vpc_endpoints[0].from_port == 443
    error_message = "Task to VPC endpoints rule must use port 443."
  }
  assert {
    condition     = aws_security_group_rule.task_to_vpc_endpoints[0].to_port == 443
    error_message = "Task to VPC endpoints rule must use port 443."
  }
}

run "test_task_to_vpc_endpoints_rule_type" {
  command = plan
  variables {
    enable_vpc_endpoint_rules = true
    vpc_endpoint_sg_id        = "sg-endpoint123"
  }
  assert {
    condition     = aws_security_group_rule.task_to_vpc_endpoints[0].type == "egress"
    error_message = "Task to VPC endpoints rule must be of type egress."
  }
}

run "test_frontend_to_vpc_endpoints_rule_port" {
  command = plan
  variables {
    enable_vpc_endpoint_rules = true
    vpc_endpoint_sg_id        = "sg-endpoint123"
  }
  assert {
    condition     = aws_security_group_rule.frontend_to_vpc_endpoints[0].from_port == 443
    error_message = "Frontend to VPC endpoints rule must use port 443."
  }
  assert {
    condition     = aws_security_group_rule.frontend_to_vpc_endpoints[0].to_port == 443
    error_message = "Frontend to VPC endpoints rule must use port 443."
  }
}

run "test_frontend_to_vpc_endpoints_rule_type" {
  command = plan
  variables {
    enable_vpc_endpoint_rules = true
    vpc_endpoint_sg_id        = "sg-endpoint123"
  }
  assert {
    condition     = aws_security_group_rule.frontend_to_vpc_endpoints[0].type == "egress"
    error_message = "Frontend to VPC endpoints rule must be of type egress."
  }
}
