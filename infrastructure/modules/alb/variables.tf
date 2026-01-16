variable "alb_sg_id" {
  description = "The security group ID for the ALB."
  type        = string
}

variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "domain_name" {
  description = "The domain name for ACM certificate (e.g., nest.owasp.dev)."
  type        = string
  default     = null
}

variable "enable_https" {
  description = "Whether to enable the HTTPS listener."
  type        = bool
  default     = false
}

variable "environment" {
  description = "The environment name (e.g., staging, production)."
  type        = string
}

variable "frontend_health_check_path" {
  description = "The health check path for the frontend target group."
  type        = string
  default     = "/"
}

variable "frontend_port" {
  description = "The port for the frontend target group."
  type        = number
  default     = 3000
}

variable "lambda_function_name" {
  description = "The name of the Lambda function for backend routing. Used to create an alias pointing to the latest published version for SnapStart support."
  type        = string
  default     = null
}

variable "log_retention_days" {
  description = "The number of days to retain ALB access logs."
  type        = number
  default     = 90
}

variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "public_subnet_ids" {
  description = "A list of public subnet IDs for the ALB."
  type        = list(string)
}

variable "vpc_id" {
  description = "The ID of the VPC."
  type        = string
}
