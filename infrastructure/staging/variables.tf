variable "availability_zones" {
  description = "A list of availability zones for the VPC."
  type        = list(string)
  default     = ["us-east-2a", "us-east-2b", "us-east-2c"]
}

variable "aws_region" {
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "us-east-2"
}

variable "create_rds_proxy" {
  description = "Whether to create an RDS proxy."
  type        = bool
  default     = false
}

variable "create_vpc_cloudwatch_logs_endpoint" {
  description = "Whether to create CloudWatch Logs VPC endpoint."
  type        = bool
  default     = false
}

variable "create_vpc_ecr_api_endpoint" {
  description = "Whether to create ECR API VPC endpoint."
  type        = bool
  default     = false
}

variable "create_vpc_ecr_dkr_endpoint" {
  description = "Whether to create ECR DKR VPC endpoint."
  type        = bool
  default     = false
}

variable "create_vpc_s3_endpoint" {
  description = "Whether to create S3 VPC endpoint (Gateway, free)."
  type        = bool
  default     = true
}

variable "create_vpc_secretsmanager_endpoint" {
  description = "Whether to create Secrets Manager VPC endpoint."
  type        = bool
  default     = false
}

variable "create_vpc_ssm_endpoint" {
  description = "Whether to create SSM VPC endpoint."
  type        = bool
  default     = false
}

variable "db_allocated_storage" {
  description = "The allocated storage for the RDS database in GB."
  type        = number
  default     = 20
}

variable "db_backup_retention_period" {
  description = "The number of days to retain backups for."
  type        = number
  default     = 7
}

variable "db_deletion_protection" {
  description = "Specifies whether to prevent database deletion."
  type        = bool
  default     = true
}

variable "db_engine_version" {
  description = "The version of the PostgreSQL engine."
  type        = string
  default     = "16.10"
}

variable "db_instance_class" {
  description = "The instance class for the RDS database."
  type        = string
  default     = "db.t3.micro"

  validation {
    condition     = can(regex("^db\\.", var.db_instance_class))
    error_message = "DB instance class must start with 'db.' (e.g., db.t3.micro, db.r5.large)."
  }
}

variable "db_name" {
  description = "The name of the RDS database."
  type        = string
  default     = "owasp_nest"
}

variable "db_password" {
  description = "The password for the RDS database."
  type        = string
  sensitive   = true
  default     = null
}

variable "db_port" {
  description = "The port for the RDS database."
  type        = number
  default     = 5432

  validation {
    condition     = var.db_port > 0 && var.db_port < 65536
    error_message = "Port must be between 1 and 65535."
  }
}

variable "db_skip_final_snapshot" {
  description = "Whether a final DB snapshot is created before the DB instance is deleted."
  type        = bool
  default     = false
}

variable "db_storage_type" {
  description = "The storage type for the RDS database."
  type        = string
  default     = "gp3"
}

variable "db_user" {
  description = "The username for the RDS database."
  type        = string
  default     = "owasp_nest_db_user"
}

variable "ecs_use_fargate_spot" {
  description = "Whether to use Fargate Spot for backend ECS tasks."
  type        = bool
  default     = true
}

variable "ecs_use_public_subnets" {
  description = "Whether to run ECS tasks in public subnets (requires assign_public_ip)."
  type        = bool
  default     = true
}

variable "environment" {
  description = "The environment (e.g., staging, production)."
  type        = string
  default     = "staging"
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Environment must be either 'staging' or 'production'."
  }
}

variable "fixtures_bucket_name" {
  description = "The name of the S3 bucket for fixtures."
  type        = string
  default     = "owasp-nest-fixtures"
}

variable "frontend_desired_count" {
  description = "The desired number of frontend tasks."
  type        = number
  default     = 2
}

variable "frontend_domain_name" {
  description = "The domain name for frontend. When set, HTTPS is auto-enabled via ACM."
  type        = string
  default     = null
}

variable "frontend_enable_auto_scaling" {
  description = "Whether to enable auto scaling for frontend."
  type        = bool
  default     = false
}

variable "frontend_max_count" {
  description = "The maximum number of tasks for auto scaling."
  type        = number
  default     = 6
}

variable "frontend_min_count" {
  description = "The minimum number of tasks for auto scaling."
  type        = number
  default     = 2
}

variable "frontend_use_fargate_spot" {
  description = "Whether to use Fargate Spot for frontend tasks."
  type        = bool
  default     = true
}

variable "lambda_arn" {
  description = "The ARN of the Zappa Lambda function for backend routing."
  type        = string
  default     = null
}

variable "lambda_function_name" {
  description = "The name of the Zappa Lambda function."
  type        = string
  default     = null
}

variable "private_subnet_cidrs" {
  description = "A list of CIDR blocks for the private subnets."
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]

  validation {
    condition = alltrue([
      for cidr in var.private_subnet_cidrs : can(cidrhost(cidr, 0))
    ])
    error_message = "All private subnet CIDRs must be valid IPv4 CIDR blocks."
  }
}

variable "project_name" {
  description = "The name of the project."
  type        = string
  default     = "nest"
}

variable "public_subnet_cidrs" {
  description = "A list of CIDR blocks for the public subnets."
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]

  validation {
    condition = alltrue([
      for cidr in var.public_subnet_cidrs : can(cidrhost(cidr, 0))
    ])
    error_message = "All public subnet CIDRs must be valid IPv4 CIDR blocks."
  }
}

variable "redis_engine_version" {
  description = "The version of the Redis engine."
  type        = string
  default     = "7.0"
}

variable "redis_node_type" {
  description = "The node type for the Redis cache."
  type        = string
  default     = "cache.t3.micro"

  validation {
    condition     = can(regex("^cache\\.", var.redis_node_type))
    error_message = "Redis node type must start with 'cache.' (e.g., cache.t3.micro, cache.r5.large)."
  }
}

variable "redis_num_cache_nodes" {
  description = "The number of cache nodes in the Redis cluster."
  type        = number
  default     = 1
}

variable "redis_port" {
  description = "The port for the Redis cache."
  type        = number
  default     = 6379

  validation {
    condition     = var.redis_port > 0 && var.redis_port < 65536
    error_message = "Port must be between 1 and 65535."
  }
}

variable "secret_recovery_window_in_days" {
  description = "The number of days that Secrets Manager waits before it can delete the secret. Set to 0 to delete immediately."
  type        = number
  default     = 7
}

variable "vpc_cidr" {
  description = "The CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid IPv4 CIDR block (e.g., 10.0.0.0/16)."
  }
}

variable "zappa_bucket_name" {
  description = "The name of the S3 bucket for Zappa deployments."
  type        = string
  default     = "owasp-nest-zappa-deployments"
}
