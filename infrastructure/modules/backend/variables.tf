variable "aws_region" {
  description = "The AWS region."
  type        = string
}

variable "backend_parameters_arns" {
  description = "Map of environment variable names to the ARNs of SSM parameters."
  type        = map(string)
  default     = {}
}

variable "backend_sg_id" {
  description = "The ID of the security group for backend ECS tasks."
  type        = string
}

variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "container_cpu" {
  description = "The number of CPU units for the backend container."
  type        = number
  default     = 1024
}

variable "container_memory" {
  description = "The amount of memory (in MiB) for the backend container."
  type        = number
  default     = 2048
}

variable "desired_count" {
  description = "The desired number of backend tasks."
  type        = number
  default     = 2
}

variable "ecr_repository_arn" {
  description = "The ARN of the ECR repository for the backend image."
  type        = string
}

variable "enable_auto_scaling" {
  description = "Whether to enable auto scaling for the backend service."
  type        = bool
  default     = false
}

variable "environment" {
  description = "The environment (e.g., staging, production)."
  type        = string
}



variable "image_url" {
  description = "The full Docker image URL including tag."
  type        = string
}

variable "kms_key_arn" {
  description = "The ARN of the KMS key for log encryption."
  type        = string
}

variable "log_retention_in_days" {
  description = "The number of days to retain CloudWatch logs."
  type        = number
  default     = 30
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
  description = "A list of private subnet IDs for the backend service."
  type        = list(string)
}

variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "target_group_arn" {
  description = "The ARN of the ALB target group for the backend."
  type        = string
}

variable "use_fargate_spot" {
  description = "Whether to use Fargate Spot capacity provider."
  type        = bool
  default     = false
}
