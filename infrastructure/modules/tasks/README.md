# Tasks

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | ~> 1.14.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 6.36.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | 6.36.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_index_data_task"></a> [index\_data\_task](#module\_index\_data\_task) | ./modules/task | n/a |
| <a name="module_load_data_task"></a> [load\_data\_task](#module\_load\_data\_task) | ./modules/task | n/a |
| <a name="module_migrate_task"></a> [migrate\_task](#module\_migrate\_task) | ./modules/task | n/a |
| <a name="module_owasp_update_project_health_metrics_task"></a> [owasp\_update\_project\_health\_metrics\_task](#module\_owasp\_update\_project\_health\_metrics\_task) | ./modules/task | n/a |
| <a name="module_owasp_update_project_health_scores_task"></a> [owasp\_update\_project\_health\_scores\_task](#module\_owasp\_update\_project\_health\_scores\_task) | ./modules/task | n/a |
| <a name="module_sync_data_task"></a> [sync\_data\_task](#module\_sync\_data\_task) | ./modules/task | n/a |

## Resources

| Name | Type |
|------|------|
| [aws_ecs_cluster.main](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ecs_cluster) | resource |
| [aws_ecs_cluster_capacity_providers.main](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ecs_cluster_capacity_providers) | resource |
| [aws_iam_policy.ecs_task_role_kms](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_policy.ecs_tasks_execution_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_policy.ecs_tasks_execution_role_ssm_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_policy.event_bridge_ecs_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_role.ecs_task_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.ecs_tasks_execution_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.event_bridge_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy_attachment.ecs_task_role_fixtures_s3_access](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.ecs_task_role_kms](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.ecs_tasks_execution_policy_attachment](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.ecs_tasks_execution_role_ssm_policy_attachment](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.event_bridge_policy_attachment](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_assign_public_ip"></a> [assign\_public\_ip](#input\_assign\_public\_ip) | Whether to assign public IPs to ECS tasks (required for public subnets). | `bool` | `false` | no |
| <a name="input_aws_region"></a> [aws\_region](#input\_aws\_region) | The AWS region. | `string` | n/a | yes |
| <a name="input_common_tags"></a> [common\_tags](#input\_common\_tags) | A map of common tags to apply to all resources. | `map(string)` | `{}` | no |
| <a name="input_container_parameters_arns"></a> [container\_parameters\_arns](#input\_container\_parameters\_arns) | Map of environment variable names to the ARNs of all SSM parameters. | `map(string)` | `{}` | no |
| <a name="input_ecr_repository_arn"></a> [ecr\_repository\_arn](#input\_ecr\_repository\_arn) | The ARN of the ECR repository for the backend image. | `string` | n/a | yes |
| <a name="input_ecr_repository_url"></a> [ecr\_repository\_url](#input\_ecr\_repository\_url) | The URL of the ECR repository for the backend image. | `string` | n/a | yes |
| <a name="input_ecs_sg_id"></a> [ecs\_sg\_id](#input\_ecs\_sg\_id) | The ID of the security group for the ECS tasks. | `string` | n/a | yes |
| <a name="input_enable_cron_tasks"></a> [enable\_cron\_tasks](#input\_enable\_cron\_tasks) | Whether to enable scheduled cron tasks. | `bool` | n/a | yes |
| <a name="input_environment"></a> [environment](#input\_environment) | The environment (e.g., staging, production). | `string` | n/a | yes |
| <a name="input_fixtures_bucket_name"></a> [fixtures\_bucket\_name](#input\_fixtures\_bucket\_name) | The name of the S3 bucket for fixtures. | `string` | n/a | yes |
| <a name="input_fixtures_read_only_policy_arn"></a> [fixtures\_read\_only\_policy\_arn](#input\_fixtures\_read\_only\_policy\_arn) | The ARN of the fixtures read-only IAM policy. | `string` | n/a | yes |
| <a name="input_image_tag"></a> [image\_tag](#input\_image\_tag) | The Docker image tag to use for ECS tasks. | `string` | n/a | yes |
| <a name="input_index_data_task_cpu"></a> [index\_data\_task\_cpu](#input\_index\_data\_task\_cpu) | The CPU for the index-data task. | `string` | `"256"` | no |
| <a name="input_index_data_task_memory"></a> [index\_data\_task\_memory](#input\_index\_data\_task\_memory) | The memory for the index-data task. | `string` | `"2048"` | no |
| <a name="input_kms_key_arn"></a> [kms\_key\_arn](#input\_kms\_key\_arn) | The ARN of the KMS key. | `string` | n/a | yes |
| <a name="input_load_data_task_cpu"></a> [load\_data\_task\_cpu](#input\_load\_data\_task\_cpu) | The CPU for the load-data task. | `string` | `"512"` | no |
| <a name="input_load_data_task_memory"></a> [load\_data\_task\_memory](#input\_load\_data\_task\_memory) | The memory for the load-data task. | `string` | `"4096"` | no |
| <a name="input_migrate_task_cpu"></a> [migrate\_task\_cpu](#input\_migrate\_task\_cpu) | The CPU for the migrate task. | `string` | `"256"` | no |
| <a name="input_migrate_task_memory"></a> [migrate\_task\_memory](#input\_migrate\_task\_memory) | The memory for the migrate task. | `string` | `"1024"` | no |
| <a name="input_project_name"></a> [project\_name](#input\_project\_name) | The name of the project. | `string` | n/a | yes |
| <a name="input_subnet_ids"></a> [subnet\_ids](#input\_subnet\_ids) | Subnet IDs for ECS tasks (can be public or private). | `list(string)` | n/a | yes |
| <a name="input_sync_data_task_cpu"></a> [sync\_data\_task\_cpu](#input\_sync\_data\_task\_cpu) | The CPU for the sync-data task. | `string` | `"256"` | no |
| <a name="input_sync_data_task_memory"></a> [sync\_data\_task\_memory](#input\_sync\_data\_task\_memory) | The memory for the sync-data task. | `string` | `"1024"` | no |
| <a name="input_update_project_health_metrics_task_cpu"></a> [update\_project\_health\_metrics\_task\_cpu](#input\_update\_project\_health\_metrics\_task\_cpu) | The CPU for the update-project-health-metrics task. | `string` | `"256"` | no |
| <a name="input_update_project_health_metrics_task_memory"></a> [update\_project\_health\_metrics\_task\_memory](#input\_update\_project\_health\_metrics\_task\_memory) | The memory for the update-project-health-metrics task. | `string` | `"1024"` | no |
| <a name="input_update_project_health_scores_task_cpu"></a> [update\_project\_health\_scores\_task\_cpu](#input\_update\_project\_health\_scores\_task\_cpu) | The CPU for the update-project-health-scores task. | `string` | `"256"` | no |
| <a name="input_update_project_health_scores_task_memory"></a> [update\_project\_health\_scores\_task\_memory](#input\_update\_project\_health\_scores\_task\_memory) | The memory for the update-project-health-scores task. | `string` | `"1024"` | no |
| <a name="input_use_fargate_spot"></a> [use\_fargate\_spot](#input\_use\_fargate\_spot) | Whether to use Fargate Spot capacity provider for cost savings. | `bool` | `false` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_ecs_cluster_arn"></a> [ecs\_cluster\_arn](#output\_ecs\_cluster\_arn) | The ARN of the ECS tasks cluster. |
| <a name="output_ecs_cluster_name"></a> [ecs\_cluster\_name](#output\_ecs\_cluster\_name) | The name of the ECS tasks cluster. |
<!-- END_TF_DOCS -->

