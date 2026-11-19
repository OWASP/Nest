<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | ~> 1.16.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 6.67.0 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_aws"></a> [aws](#provider\_aws) | 6.67.0 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [aws_ecs_service.main](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ecs_service) | resource |
| [aws_ecs_task_definition.main](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ecs_task_definition) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_command"></a> [command](#input\_command) | Command executed by the worker. | `list(string)` | n/a | yes |
| <a name="input_common_tags"></a> [common\_tags](#input\_common\_tags) | Tags applied to worker resources. | `map(string)` | `{}` | no |
| <a name="input_container_name"></a> [container\_name](#input\_container\_name) | Worker container name. | `string` | n/a | yes |
| <a name="input_desired_count"></a> [desired\_count](#input\_desired\_count) | Desired number of worker tasks. | `number` | n/a | yes |
| <a name="input_force_new_deployment"></a> [force\_new\_deployment](#input\_force\_new\_deployment) | Whether to force a new deployment on each apply. | `bool` | `false` | no |
| <a name="input_health_check_command"></a> [health\_check\_command](#input\_health\_check\_command) | ECS worker health check command. | `list(string)` | n/a | yes |
| <a name="input_name_prefix"></a> [name\_prefix](#input\_name\_prefix) | Prefix for the worker task family and service name. | `string` | n/a | yes |
| <a name="input_private_subnet_ids"></a> [private\_subnet\_ids](#input\_private\_subnet\_ids) | Private subnet IDs for worker tasks. | `list(string)` | n/a | yes |
| <a name="input_security_group_id"></a> [security\_group\_id](#input\_security\_group\_id) | Security group ID for worker tasks. | `string` | n/a | yes |
| <a name="input_task_context"></a> [task\_context](#input\_task\_context) | Shared image, container configuration, cluster, roles and task size from the parent service. | <pre>object({<br/>    cluster_arn          = string<br/>    execution_role_arn   = string<br/>    task_role_arn        = string<br/>    cpu                  = number<br/>    memory               = number<br/>    container_definition = any<br/>  })</pre> | n/a | yes |
| <a name="input_use_fargate_spot"></a> [use\_fargate\_spot](#input\_use\_fargate\_spot) | Whether to use Fargate Spot capacity. | `bool` | `false` | no |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_container_environment"></a> [container\_environment](#output\_container\_environment) | Explicit environment variables passed to the worker container. |
| <a name="output_ecs_service_name"></a> [ecs\_service\_name](#output\_ecs\_service\_name) | The worker ECS service name. |
<!-- END_TF_DOCS -->
