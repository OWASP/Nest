variable "app_security_group_ids" {
  description = "Security group IDs of the application tasks allowed to send metrics to VictoriaMetrics."
  type        = list(string)
}

variable "assign_public_ip" {
  description = "Whether to assign a public IP to the VictoriaMetrics task."
  type        = bool
  default     = false
}

variable "aws_region" {
  description = "The AWS region where the module is deployed."
  type        = string
}

variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "environment" {
  description = "The environment (e.g., staging, production)."
  type        = string
}

variable "kms_key_arn" {
  description = "The ARN of the KMS key used to encrypt the EFS file system."
  type        = string
}

variable "log_retention_in_days" {
  description = "The number of days to retain VictoriaMetrics container logs."
  type        = number
  default     = 90
}

variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "subnet_ids" {
  description = "The private subnet IDs for the EFS mount targets and the VictoriaMetrics task."
  type        = list(string)
}

variable "vm_cpu" {
  description = "The CPU units for the VictoriaMetrics Fargate task."
  type        = number
  default     = 512
}

variable "vm_image" {
  description = "The VictoriaMetrics container image (including digest)."
  type        = string
}

variable "vm_memory" {
  description = "The memory (in MiB) for the VictoriaMetrics Fargate task."
  type        = number
  default     = 1024
}

variable "vm_port" {
  description = "The port VictoriaMetrics listens on for ingest and queries."
  type        = number
  default     = 8428
}

variable "vm_retention_period" {
  description = "The VictoriaMetrics data retention period (e.g., 12, 5y)."
  type        = string
  default     = "12"
}

variable "vpc_id" {
  description = "The VPC ID where the VictoriaMetrics security group is created."
  type        = string
}
