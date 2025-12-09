variable "alb_sg_id" {
  description = "The security group ID for the ALB."
  type        = string
}

variable "aws_region" {
  description = "The AWS region for resources."
  type        = string
}

variable "common_tags" {
  description = "The common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "container_cpu" {
  description = "The CPU units for the frontend container (1024 = 1 vCPU)."
  type        = number
  default     = 512
}

variable "container_memory" {
  description = "The memory for the frontend container in MB."
  type        = number
  default     = 1024
}

variable "desired_count" {
  description = "The desired number of frontend tasks."
  type        = number
  default     = 2
}

variable "domain_name" {
  description = "The domain name for the frontend (required for HTTPS)."
  type        = string
  default     = null
}

variable "enable_auto_scaling" {
  description = "Whether to enable auto scaling for the frontend."
  type        = bool
  default     = false
}

variable "enable_https" {
  description = "Whether to enable the HTTPS listener on the ALB."
  type        = bool
  default     = false
}

variable "environment" {
  description = "The environment name (staging, production)."
  type        = string
}

variable "frontend_parameters_arns" {
  description = "A map of environment variable names to SSM parameter ARNs."
  type        = map(string)
}

variable "frontend_sg_id" {
  description = "The security group ID for the frontend ECS tasks."
  type        = string
}

variable "health_check_path" {
  description = "The health check path for the frontend."
  type        = string
  default     = "/"
}

variable "image_tag" {
  description = "The Docker image tag for the frontend."
  type        = string
  default     = "latest"
}

variable "log_retention_in_days" {
  description = "The CloudWatch log retention in days."
  type        = number
  default     = 7
}

variable "max_count" {
  description = "The maximum number of tasks for auto scaling."
  type        = number
  default     = 6
}

variable "min_count" {
  description = "The minimum number of tasks for auto scaling."
  type        = number
  default     = 2
}

variable "private_subnet_ids" {
  description = "The list of private subnet IDs for ECS tasks."
  type        = list(string)
}

variable "project_name" {
  description = "The project name."
  type        = string
}

variable "public_subnet_ids" {
  description = "The list of public subnet IDs for the ALB."
  type        = list(string)
}

variable "vpc_id" {
  description = "The VPC ID."
  type        = string
}
