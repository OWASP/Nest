variable "availability_zones" {
  description = "A list of availability zones for the VPC"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "db_allocated_storage" {
  description = "The allocated storage for the RDS database in GB"
  type        = number
  default     = 20
}

variable "db_engine_version" {
  description = "The version of the PostgreSQL engine"
  type        = string
  default     = "16.10"
}

variable "db_instance_class" {
  description = "The instance class for the RDS database"
  type        = string
  default     = "db.t3.micro"
}

variable "db_name" {
  description = "The name of the RDS database"
  type        = string
  default     = "nestdb"
}

variable "db_password" {
  description = "The password for the RDS database"
  type        = string
  sensitive   = true
  default     = null
}

variable "db_port" {
  description = "The port for the RDS database"
  type        = number
  default     = 5432
}

variable "db_username" {
  description = "The username for the RDS database"
  type        = string
  default     = "nestuser"
}

variable "environment" {
  description = "The environment (e.g., staging, production)"
  type        = string
  default     = "staging"
}

variable "private_subnet_cidrs" {
  description = "A list of CIDR blocks for the private subnets"
  type        = list(string)
  default     = ["10.0.3.0/24", "10.0.4.0/24"]
}

variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "nest"
}

variable "public_subnet_cidrs" {
  description = "A list of CIDR blocks for the public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "redis_auth_token" {
  description = "The auth token for Redis"
  type        = string
  sensitive   = true
  default     = null
}

variable "redis_engine_version" {
  description = "The version of the Redis engine"
  type        = string
  default     = "7.0"
}

variable "redis_node_type" {
  description = "The node type for the Redis cache"
  type        = string
  default     = "cache.t3.micro"
}

variable "redis_num_cache_nodes" {
  description = "The number of cache nodes in the Redis cluster"
  type        = number
  default     = 1
}

variable "redis_port" {
  description = "The port for the Redis cache"
  type        = number
  default     = 6379
}

variable "vpc_cidr" {
  description = "The CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "zappa_s3_bucket" {
  description = "The name of the S3 bucket for Zappa deployments"
  type        = string
  default     = "nest-zappa-deployments"
}
