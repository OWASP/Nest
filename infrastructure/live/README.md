## Prerequisites

Before the first **staging** CI/CD run you must:

1. **IAM role `nest-staging-terraform` (lifecycle)**
   The staging pipeline assumes this role (see the "STSStateManagement" resource below). The role is **created automatically** by the bootstrap when you run it (e.g. the bootstrap workflow that applies `infrastructure/bootstrap` with `staging` in the environments list). On first deployment, the bootstrap run creates `aws_iam_role.terraform` (named `${project}-${env}-terraform`, here `nest-staging-terraform`); subsequent bootstrap runs **update** the existing role. No code or workflow changes are required for this.
   **Manual intervention** may still be needed if you delete the role in AWS, remove it from Terraform state, or need to change the ExternalId (e.g. in the role trust policy or in the staging pipeline configuration).

2. **Create the `nest-staging` IAM user** and attach the inline permissions documented below. This user is used to assume the `nest-staging-terraform` role.

3. **Ensure backend resources exist** and replace the placeholders in the policy and pipeline configuration:
   - **AWS_ACCOUNT_ID** — Your AWS account ID (used in the role ARN).

## Inline Permissions

Use the following inline permissions for the `nest-staging` IAM User.
*Note*: replace the placeholder `AWS_ACCOUNT_ID` with the appropriate value before running the pipeline.

```json
{
    "Version": "2012-10-17",
        "Statement": [
        {
            "Sid": "STSStateManagement",
            "Effect": "Allow",
            "Action": [
                "sts:AssumeRole",
                "sts:TagSession"
            ],
            "Resource": "arn:aws:iam::AWS_ACCOUNT_ID:role/nest-staging-terraform"
        }
    ]
}
```

## Terraform Reference

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | ~> 1.14.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 6.36.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_alb"></a> [alb](#module\_alb) | ../modules/alb | n/a |
| <a name="module_backend"></a> [backend](#module\_backend) | ../modules/service | n/a |
| <a name="module_cache"></a> [cache](#module\_cache) | ../modules/cache | n/a |
| <a name="module_database"></a> [database](#module\_database) | ../modules/database | n/a |
| <a name="module_frontend"></a> [frontend](#module\_frontend) | ../modules/service | n/a |
| <a name="module_kms"></a> [kms](#module\_kms) | ../modules/kms | n/a |
| <a name="module_networking"></a> [networking](#module\_networking) | ../modules/networking | n/a |
| <a name="module_parameters"></a> [parameters](#module\_parameters) | ../modules/parameters | n/a |
| <a name="module_security"></a> [security](#module\_security) | ../modules/security | n/a |
| <a name="module_storage"></a> [storage](#module\_storage) | ../modules/storage | n/a |
| <a name="module_tasks"></a> [tasks](#module\_tasks) | ../modules/tasks | n/a |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_availability_zones"></a> [availability\_zones](#input\_availability\_zones) | A list of availability zones for the VPC. | `list(string)` | ```[ "us-east-2a", "us-east-2b", "us-east-2c" ]``` | no |
| <a name="input_aws_region"></a> [aws\_region](#input\_aws\_region) | The AWS region to deploy resources in. | `string` | `"us-east-2"` | no |
| <a name="input_backend_desired_count"></a> [backend\_desired\_count](#input\_backend\_desired\_count) | The desired number of backend tasks. | `number` | `1` | no |
| <a name="input_backend_enable_auto_scaling"></a> [backend\_enable\_auto\_scaling](#input\_backend\_enable\_auto\_scaling) | Whether to enable auto scaling for backend. | `bool` | `false` | no |
| <a name="input_backend_image_tag"></a> [backend\_image\_tag](#input\_backend\_image\_tag) | The Docker backend image tag. | `string` | n/a | yes |
| <a name="input_backend_max_count"></a> [backend\_max\_count](#input\_backend\_max\_count) | The maximum number of backend tasks for auto scaling. | `number` | `6` | no |
| <a name="input_backend_min_count"></a> [backend\_min\_count](#input\_backend\_min\_count) | The minimum number of backend tasks for auto scaling. | `number` | `2` | no |
| <a name="input_backend_use_fargate_spot"></a> [backend\_use\_fargate\_spot](#input\_backend\_use\_fargate\_spot) | Whether to use Fargate Spot for backend tasks. | `bool` | `true` | no |
| <a name="input_db_allocated_storage"></a> [db\_allocated\_storage](#input\_db\_allocated\_storage) | The allocated storage for the RDS database in GB. | `number` | `20` | no |
| <a name="input_db_backup_retention_period"></a> [db\_backup\_retention\_period](#input\_db\_backup\_retention\_period) | The number of days to retain backups for. | `number` | `7` | no |
| <a name="input_db_deletion_protection"></a> [db\_deletion\_protection](#input\_db\_deletion\_protection) | Specifies whether to prevent database deletion. | `bool` | `true` | no |
| <a name="input_db_engine_version"></a> [db\_engine\_version](#input\_db\_engine\_version) | The version of the PostgreSQL engine. | `string` | `"16.10"` | no |
| <a name="input_db_instance_class"></a> [db\_instance\_class](#input\_db\_instance\_class) | The instance class for the RDS database. | `string` | `"db.t3.micro"` | no |
| <a name="input_db_name"></a> [db\_name](#input\_db\_name) | The name of the RDS database. | `string` | `"nest_db"` | no |
| <a name="input_db_password"></a> [db\_password](#input\_db\_password) | The password for the RDS database. | `string` | `null` | no |
| <a name="input_db_port"></a> [db\_port](#input\_db\_port) | The port for the RDS database. | `number` | `5432` | no |
| <a name="input_db_skip_final_snapshot"></a> [db\_skip\_final\_snapshot](#input\_db\_skip\_final\_snapshot) | Whether a final DB snapshot is created before the DB instance is deleted. | `bool` | `false` | no |
| <a name="input_db_storage_type"></a> [db\_storage\_type](#input\_db\_storage\_type) | The storage type for the RDS database. | `string` | `"gp3"` | no |
| <a name="input_db_user"></a> [db\_user](#input\_db\_user) | The username for the RDS database. | `string` | `"nest_db_user"` | no |
| <a name="input_django_configuration"></a> [django\_configuration](#input\_django\_configuration) | The name of the Django configuration to use (e.g., Staging, Production). | `string` | n/a | yes |
| <a name="input_django_release_version"></a> [django\_release\_version](#input\_django\_release\_version) | The Django release version. | `string` | `"0.0.0"` | no |
| <a name="input_django_settings_module"></a> [django\_settings\_module](#input\_django\_settings\_module) | The location of the Django settings module to use (e.g., settings.staging, settings.production). | `string` | n/a | yes |
| <a name="input_domain_name"></a> [domain\_name](#input\_domain\_name) | The domain name for the site. | `string` | n/a | yes |
| <a name="input_enable_additional_parameters"></a> [enable\_additional\_parameters](#input\_enable\_additional\_parameters) | Whether to enable additional parameters (e.g. for production). | `bool` | `false` | no |
| <a name="input_enable_cron_tasks"></a> [enable\_cron\_tasks](#input\_enable\_cron\_tasks) | Whether to enable scheduled cron tasks. | `bool` | n/a | yes |
| <a name="input_enable_nat_gateway"></a> [enable\_nat\_gateway](#input\_enable\_nat\_gateway) | Whether to enable a NAT Gateway. | `bool` | `true` | no |
| <a name="input_enable_rds_proxy"></a> [enable\_rds\_proxy](#input\_enable\_rds\_proxy) | Whether to create an RDS proxy. | `bool` | `false` | no |
| <a name="input_enable_vpc_cloudwatch_logs_endpoint"></a> [enable\_vpc\_cloudwatch\_logs\_endpoint](#input\_enable\_vpc\_cloudwatch\_logs\_endpoint) | Whether to create CloudWatch Logs VPC endpoint. | `bool` | `false` | no |
| <a name="input_enable_vpc_ecr_api_endpoint"></a> [enable\_vpc\_ecr\_api\_endpoint](#input\_enable\_vpc\_ecr\_api\_endpoint) | Whether to create ECR API VPC endpoint. | `bool` | `false` | no |
| <a name="input_enable_vpc_ecr_dkr_endpoint"></a> [enable\_vpc\_ecr\_dkr\_endpoint](#input\_enable\_vpc\_ecr\_dkr\_endpoint) | Whether to create ECR DKR VPC endpoint. | `bool` | `false` | no |
| <a name="input_enable_vpc_s3_endpoint"></a> [enable\_vpc\_s3\_endpoint](#input\_enable\_vpc\_s3\_endpoint) | Whether to create S3 VPC endpoint (Gateway, free). | `bool` | `true` | no |
| <a name="input_enable_vpc_secretsmanager_endpoint"></a> [enable\_vpc\_secretsmanager\_endpoint](#input\_enable\_vpc\_secretsmanager\_endpoint) | Whether to create Secrets Manager VPC endpoint. | `bool` | `false` | no |
| <a name="input_enable_vpc_ssm_endpoint"></a> [enable\_vpc\_ssm\_endpoint](#input\_enable\_vpc\_ssm\_endpoint) | Whether to create SSM VPC endpoint. | `bool` | `false` | no |
| <a name="input_environment"></a> [environment](#input\_environment) | The environment (e.g., staging, production). | `string` | n/a | yes |
| <a name="input_fixtures_bucket_name"></a> [fixtures\_bucket\_name](#input\_fixtures\_bucket\_name) | The name of the S3 bucket for fixtures. | `string` | `null` | no |
| <a name="input_frontend_desired_count"></a> [frontend\_desired\_count](#input\_frontend\_desired\_count) | The desired number of frontend tasks. | `number` | `1` | no |
| <a name="input_frontend_enable_auto_scaling"></a> [frontend\_enable\_auto\_scaling](#input\_frontend\_enable\_auto\_scaling) | Whether to enable auto scaling for frontend. | `bool` | `false` | no |
| <a name="input_frontend_image_tag"></a> [frontend\_image\_tag](#input\_frontend\_image\_tag) | The Docker frontend image tag. | `string` | n/a | yes |
| <a name="input_frontend_max_count"></a> [frontend\_max\_count](#input\_frontend\_max\_count) | The maximum number of tasks for auto scaling. | `number` | `6` | no |
| <a name="input_frontend_min_count"></a> [frontend\_min\_count](#input\_frontend\_min\_count) | The minimum number of tasks for auto scaling. | `number` | `2` | no |
| <a name="input_frontend_use_fargate_spot"></a> [frontend\_use\_fargate\_spot](#input\_frontend\_use\_fargate\_spot) | Whether to use Fargate Spot for frontend tasks. | `bool` | `true` | no |
| <a name="input_private_subnet_cidrs"></a> [private\_subnet\_cidrs](#input\_private\_subnet\_cidrs) | A list of CIDR blocks for the private subnets. | `list(string)` | ```[ "10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24" ]``` | no |
| <a name="input_project_name"></a> [project\_name](#input\_project\_name) | The name of the project. | `string` | `"nest"` | no |
| <a name="input_public_subnet_cidrs"></a> [public\_subnet\_cidrs](#input\_public\_subnet\_cidrs) | A list of CIDR blocks for the public subnets. | `list(string)` | ```[ "10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24" ]``` | no |
| <a name="input_redis_engine_version"></a> [redis\_engine\_version](#input\_redis\_engine\_version) | The version of the Redis engine. | `string` | `"7.0"` | no |
| <a name="input_redis_node_type"></a> [redis\_node\_type](#input\_redis\_node\_type) | The node type for the Redis cache. | `string` | `"cache.t3.micro"` | no |
| <a name="input_redis_num_cache_nodes"></a> [redis\_num\_cache\_nodes](#input\_redis\_num\_cache\_nodes) | The number of cache nodes in the Redis cluster. | `number` | `1` | no |
| <a name="input_redis_port"></a> [redis\_port](#input\_redis\_port) | The port for the Redis cache. | `number` | `6379` | no |
| <a name="input_secret_recovery_window_in_days"></a> [secret\_recovery\_window\_in\_days](#input\_secret\_recovery\_window\_in\_days) | The number of days that Secrets Manager waits before it can delete the secret. Set to 0 to delete immediately. | `number` | `7` | no |
| <a name="input_slack_bot_token_suffix"></a> [slack\_bot\_token\_suffix](#input\_slack\_bot\_token\_suffix) | The Suffix for the Slack bot token. | `string` | `"T04T40NHX"` | no |
| <a name="input_tasks_use_fargate_spot"></a> [tasks\_use\_fargate\_spot](#input\_tasks\_use\_fargate\_spot) | Whether to use Fargate Spot for ECS tasks. | `bool` | `true` | no |
| <a name="input_vpc_cidr"></a> [vpc\_cidr](#input\_vpc\_cidr) | The CIDR block for the VPC. | `string` | `"10.0.0.0/16"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_acm_certificate_domain_validation_options"></a> [acm\_certificate\_domain\_validation\_options](#output\_acm\_certificate\_domain\_validation\_options) | The DNS validation options for ACM certificate. |
| <a name="output_acm_certificate_status"></a> [acm\_certificate\_status](#output\_acm\_certificate\_status) | The status of the ACM certificate. |
| <a name="output_alb_dns_name"></a> [alb\_dns\_name](#output\_alb\_dns\_name) | The DNS name of the ALB. |
| <a name="output_backend_cluster_name"></a> [backend\_cluster\_name](#output\_backend\_cluster\_name) | The name of the ECS backend cluster. |
| <a name="output_backend_ecr_repository_url"></a> [backend\_ecr\_repository\_url](#output\_backend\_ecr\_repository\_url) | The URL of the backend ECR repository. |
| <a name="output_backend_service_name"></a> [backend\_service\_name](#output\_backend\_service\_name) | The name of the ECS backend service. |
| <a name="output_fixtures_bucket_name"></a> [fixtures\_bucket\_name](#output\_fixtures\_bucket\_name) | The name of the S3 bucket for database fixtures. |
| <a name="output_frontend_cluster_name"></a> [frontend\_cluster\_name](#output\_frontend\_cluster\_name) | The name of the ECS frontend cluster. |
| <a name="output_frontend_ecr_repository_url"></a> [frontend\_ecr\_repository\_url](#output\_frontend\_ecr\_repository\_url) | The URL of the frontend ECR repository. |
| <a name="output_frontend_service_name"></a> [frontend\_service\_name](#output\_frontend\_service\_name) | The name of the ECS frontend service. |
| <a name="output_frontend_url"></a> [frontend\_url](#output\_frontend\_url) | The URL to access the frontend. |
| <a name="output_nat_gateway_enabled"></a> [nat\_gateway\_enabled](#output\_nat\_gateway\_enabled) | Whether a NAT Gateway is enabled. |
| <a name="output_private_subnet_ids"></a> [private\_subnet\_ids](#output\_private\_subnet\_ids) | A list of private subnet IDs. |
| <a name="output_tasks_cluster_name"></a> [tasks\_cluster\_name](#output\_tasks\_cluster\_name) | The name of the ECS tasks cluster. |
| <a name="output_tasks_security_group_id"></a> [tasks\_security\_group\_id](#output\_tasks\_security\_group\_id) | The ID of the security group for ECS tasks. |
| <a name="output_tasks_subnet_ids"></a> [tasks\_subnet\_ids](#output\_tasks\_subnet\_ids) | A list of public or private subnet IDs for ECS tasks. |
<!-- END_TF_DOCS -->

