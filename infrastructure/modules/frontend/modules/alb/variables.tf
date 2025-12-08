variable "acm_certificate_arn" {
  description = "The ACM certificate ARN for HTTPS."
  type        = string
  default     = null
}

variable "alb_sg_id" {
  description = "The security group ID for the ALB."
  type        = string
}

variable "common_tags" {
  description = "The common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "enable_https" {
  description = "Whether to enable the HTTPS listener."
  type        = bool
  default     = false
}

variable "environment" {
  description = "The environment name."
  type        = string
}

variable "health_check_path" {
  description = "The health check path."
  type        = string
  default     = "/"
}

variable "log_retention_days" {
  description = "The number of days to retain ALB access logs."
  type        = number
  default     = 90
}

variable "project_name" {
  description = "The project name."
  type        = string
}

variable "public_subnet_ids" {
  description = "The list of public subnet IDs."
  type        = list(string)
}

variable "vpc_id" {
  description = "The VPC ID."
  type        = string
}
