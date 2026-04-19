<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | ~> 1.14.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 6.36.0 |
| <a name="requirement_random"></a> [random](#requirement\_random) | ~> 3.8.0 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_aws"></a> [aws](#provider\_aws) | 6.36.0 |
| <a name="provider_random"></a> [random](#provider\_random) | 3.8.1 |

## Modules

No modules.

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_auto_minor_version_upgrade"></a> [auto\_minor\_version\_upgrade](#input\_auto\_minor\_version\_upgrade) | Whether minor engine upgrades will be applied automatically. | `bool` | `true` | no |
| <a name="input_common_tags"></a> [common\_tags](#input\_common\_tags) | A map of common tags to apply to all resources. | `map(string)` | `{}` | no |
| <a name="input_environment"></a> [environment](#input\_environment) | The environment (e.g., staging, production). | `string` | n/a | yes |
| <a name="input_kms_key_arn"></a> [kms\_key\_arn](#input\_kms\_key\_arn) | The ARN of the KMS key. | `string` | n/a | yes |
| <a name="input_log_retention_in_days"></a> [log\_retention\_in\_days](#input\_log\_retention\_in\_days) | The number of days to retain log events. | `number` | `90` | no |
| <a name="input_maintenance_window"></a> [maintenance\_window](#input\_maintenance\_window) | The weekly time range for when maintenance on the cache cluster is performed. | `string` | `"mon:05:00-mon:07:00"` | no |
| <a name="input_project_name"></a> [project\_name](#input\_project\_name) | The name of the project. | `string` | n/a | yes |
| <a name="input_redis_engine_version"></a> [redis\_engine\_version](#input\_redis\_engine\_version) | The version of the Redis engine. | `string` | n/a | yes |
| <a name="input_redis_node_type"></a> [redis\_node\_type](#input\_redis\_node\_type) | The node type for the Redis cache. | `string` | n/a | yes |
| <a name="input_redis_num_cache_nodes"></a> [redis\_num\_cache\_nodes](#input\_redis\_num\_cache\_nodes) | The number of cache nodes in the Redis cluster. | `number` | n/a | yes |
| <a name="input_redis_port"></a> [redis\_port](#input\_redis\_port) | The port for the Redis cache. | `number` | n/a | yes |
| <a name="input_security_group_ids"></a> [security\_group\_ids](#input\_security\_group\_ids) | A list of security group IDs to associate with the Redis cache. | `list(string)` | n/a | yes |
| <a name="input_snapshot_retention_limit"></a> [snapshot\_retention\_limit](#input\_snapshot\_retention\_limit) | The number of days for which automatic snapshots are retained. | `number` | `5` | no |
| <a name="input_snapshot_window"></a> [snapshot\_window](#input\_snapshot\_window) | The daily time range (in UTC) during which ElastiCache will begin taking a daily snapshot. | `string` | `"03:00-05:00"` | no |
| <a name="input_subnet_ids"></a> [subnet\_ids](#input\_subnet\_ids) | A list of subnet IDs for the cache subnet group. | `list(string)` | n/a | yes |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_redis_password_arn"></a> [redis\_password\_arn](#output\_redis\_password\_arn) | The SSM Parameter ARN of password of Redis. |
| <a name="output_redis_primary_endpoint"></a> [redis\_primary\_endpoint](#output\_redis\_primary\_endpoint) | The primary endpoint of the Redis replication group. |
<!-- END_TF_DOCS -->
