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

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_common_tags"></a> [common\_tags](#input\_common\_tags) | A map of common tags to apply to all resources. | `map(string)` | `{}` | no |
| <a name="input_db_port"></a> [db\_port](#input\_db\_port) | The port for the RDS database. | `number` | n/a | yes |
| <a name="input_enable_rds_proxy"></a> [enable\_rds\_proxy](#input\_enable\_rds\_proxy) | Whether to create an RDS proxy. | `bool` | `false` | no |
| <a name="input_enable_vpc_endpoint_rules"></a> [enable\_vpc\_endpoint\_rules](#input\_enable\_vpc\_endpoint\_rules) | Whether to create security group rules for VPC endpoints. | `bool` | `false` | no |
| <a name="input_environment"></a> [environment](#input\_environment) | The environment (e.g., staging, production). | `string` | n/a | yes |
| <a name="input_project_name"></a> [project\_name](#input\_project\_name) | The name of the project. | `string` | n/a | yes |
| <a name="input_redis_port"></a> [redis\_port](#input\_redis\_port) | The port for the Redis cache. | `number` | n/a | yes |
| <a name="input_vpc_endpoint_sg_id"></a> [vpc\_endpoint\_sg\_id](#input\_vpc\_endpoint\_sg\_id) | Security group ID for VPC endpoints (null if VPC endpoints disabled). | `string` | `null` | no |
| <a name="input_vpc_id"></a> [vpc\_id](#input\_vpc\_id) | The ID of the VPC. | `string` | n/a | yes |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_alb_sg_id"></a> [alb\_sg\_id](#output\_alb\_sg\_id) | The ID of the ALB security group. |
| <a name="output_backend_sg_id"></a> [backend\_sg\_id](#output\_backend\_sg\_id) | The ID of the backend ECS security group. |
| <a name="output_frontend_sg_id"></a> [frontend\_sg\_id](#output\_frontend\_sg\_id) | The ID of the frontend ECS security group. |
| <a name="output_rds_proxy_sg_id"></a> [rds\_proxy\_sg\_id](#output\_rds\_proxy\_sg\_id) | The ID of the RDS proxy security group. |
| <a name="output_rds_sg_id"></a> [rds\_sg\_id](#output\_rds\_sg\_id) | The ID of the RDS security group. |
| <a name="output_redis_sg_id"></a> [redis\_sg\_id](#output\_redis\_sg\_id) | The ID of the Redis security group. |
| <a name="output_tasks_sg_id"></a> [tasks\_sg\_id](#output\_tasks\_sg\_id) | The ID of the ECS tasks security group. |
<!-- END_TF_DOCS -->
