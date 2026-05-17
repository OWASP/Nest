<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | ~> 1.14.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 6.36.0 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_aws"></a> [aws](#provider\_aws) | 6.36.0 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [aws_cloudwatch_event_rule.task](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule) | resource |
| [aws_cloudwatch_event_target.task](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_target) | resource |
| [aws_cloudwatch_log_group.task](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group) | resource |
| [aws_ecs_task_definition.task](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ecs_task_definition) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_assign_public_ip"></a> [assign\_public\_ip](#input\_assign\_public\_ip) | Whether to assign public IPs to ECS tasks. | `bool` | `false` | no |
| <a name="input_aws_region"></a> [aws\_region](#input\_aws\_region) | The AWS region for the CloudWatch logs. | `string` | n/a | yes |
| <a name="input_command"></a> [command](#input\_command) | The command to run in the container. | `list(string)` | n/a | yes |
| <a name="input_common_tags"></a> [common\_tags](#input\_common\_tags) | A map of common tags to apply to all resources. | `map(string)` | `{}` | no |
| <a name="input_container_parameters_arns"></a> [container\_parameters\_arns](#input\_container\_parameters\_arns) | A Map of environment variable names to the ARNs of all SSM parameters. | `map(string)` | `{}` | no |
| <a name="input_cpu"></a> [cpu](#input\_cpu) | The CPU units to allocate for the task. | `string` | n/a | yes |
| <a name="input_ecs_cluster_arn"></a> [ecs\_cluster\_arn](#input\_ecs\_cluster\_arn) | The ARN of the ECS cluster. | `string` | n/a | yes |
| <a name="input_ecs_tasks_execution_role_arn"></a> [ecs\_tasks\_execution\_role\_arn](#input\_ecs\_tasks\_execution\_role\_arn) | The ARN of the ECS task execution role. | `string` | n/a | yes |
| <a name="input_environment"></a> [environment](#input\_environment) | The environment (e.g., staging, production). | `string` | n/a | yes |
| <a name="input_event_bridge_role_arn"></a> [event\_bridge\_role\_arn](#input\_event\_bridge\_role\_arn) | The ARN of the EventBridge role to trigger the task. Only required for scheduled tasks. | `string` | `null` | no |
| <a name="input_image_url"></a> [image\_url](#input\_image\_url) | The URL of the ECR image to run. | `string` | n/a | yes |
| <a name="input_kms_key_arn"></a> [kms\_key\_arn](#input\_kms\_key\_arn) | The ARN of the KMS key. | `string` | n/a | yes |
| <a name="input_log_retention_in_days"></a> [log\_retention\_in\_days](#input\_log\_retention\_in\_days) | The number of days to retain log events. | `number` | `90` | no |
| <a name="input_memory"></a> [memory](#input\_memory) | The memory (in MiB) to allocate for the task. | `string` | n/a | yes |
| <a name="input_project_name"></a> [project\_name](#input\_project\_name) | The name of the project. | `string` | n/a | yes |
| <a name="input_schedule_expression"></a> [schedule\_expression](#input\_schedule\_expression) | The cron expression for the schedule. If null, the task is not scheduled. | `string` | `null` | no |
| <a name="input_security_group_ids"></a> [security\_group\_ids](#input\_security\_group\_ids) | A list of security group IDs to associate with the task. | `list(string)` | n/a | yes |
| <a name="input_subnet_ids"></a> [subnet\_ids](#input\_subnet\_ids) | Subnet IDs for the task (can be public or private). | `list(string)` | n/a | yes |
| <a name="input_task_name"></a> [task\_name](#input\_task\_name) | The unique name of the task. | `string` | n/a | yes |
| <a name="input_task_role_arn"></a> [task\_role\_arn](#input\_task\_role\_arn) | The ARN of the IAM role for the task. | `string` | `null` | no |
| <a name="input_use_fargate_spot"></a> [use\_fargate\_spot](#input\_use\_fargate\_spot) | Whether to use Fargate Spot capacity provider. | `bool` | `false` | no |

## Outputs

No outputs.
<!-- END_TF_DOCS -->
