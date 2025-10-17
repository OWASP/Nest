variable "db_port" {
  description = "The port for the RDS database"
  type        = number
}

variable "environment" {
  description = "The environment (e.g., staging, production)"
  type        = string
}

variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "redis_port" {
  description = "The port for the Redis cache"
  type        = number
}

variable "vpc_id" {
  description = "The ID of the VPC"
  type        = string
}
