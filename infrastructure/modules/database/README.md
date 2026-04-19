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
| <a name="input_common_tags"></a> [common\_tags](#input\_common\_tags) | A map of common tags to apply to all resources. | `map(string)` | `{}` | no |
| <a name="input_db_allocated_storage"></a> [db\_allocated\_storage](#input\_db\_allocated\_storage) | The allocated storage for the RDS database in GB. | `number` | n/a | yes |
| <a name="input_db_backup_retention_period"></a> [db\_backup\_retention\_period](#input\_db\_backup\_retention\_period) | The number of days to retain backups for. | `number` | `7` | no |
| <a name="input_db_backup_window"></a> [db\_backup\_window](#input\_db\_backup\_window) | The daily time range (in UTC) during which automated backups are created. | `string` | `"03:00-04:00"` | no |
| <a name="input_db_copy_tags_to_snapshot"></a> [db\_copy\_tags\_to\_snapshot](#input\_db\_copy\_tags\_to\_snapshot) | Whether to copy all instance tags to snapshots. | `bool` | `true` | no |
| <a name="input_db_deletion_protection"></a> [db\_deletion\_protection](#input\_db\_deletion\_protection) | Specifies whether to prevent database deletion. | `bool` | `true` | no |
| <a name="input_db_engine_version"></a> [db\_engine\_version](#input\_db\_engine\_version) | The version of the PostgreSQL engine. | `string` | n/a | yes |
| <a name="input_db_instance_class"></a> [db\_instance\_class](#input\_db\_instance\_class) | The instance class for the RDS database. | `string` | n/a | yes |
| <a name="input_db_maintenance_window"></a> [db\_maintenance\_window](#input\_db\_maintenance\_window) | The weekly time range (in UTC) during which system maintenance can occur. | `string` | `"mon:04:00-mon:05:00"` | no |
| <a name="input_db_name"></a> [db\_name](#input\_db\_name) | The name of the RDS database. | `string` | n/a | yes |
| <a name="input_db_password"></a> [db\_password](#input\_db\_password) | The password for the RDS database. | `string` | `null` | no |
| <a name="input_db_skip_final_snapshot"></a> [db\_skip\_final\_snapshot](#input\_db\_skip\_final\_snapshot) | Whether a final DB snapshot is created before the DB instance is deleted. | `bool` | `false` | no |
| <a name="input_db_storage_type"></a> [db\_storage\_type](#input\_db\_storage\_type) | The storage type for the RDS database. | `string` | `"gp3"` | no |
| <a name="input_db_subnet_ids"></a> [db\_subnet\_ids](#input\_db\_subnet\_ids) | A list of subnet IDs for the DB subnet group. | `list(string)` | n/a | yes |
| <a name="input_db_user"></a> [db\_user](#input\_db\_user) | The username for the RDS database. | `string` | n/a | yes |
| <a name="input_enable_rds_proxy"></a> [enable\_rds\_proxy](#input\_enable\_rds\_proxy) | Whether to create an RDS proxy. | `bool` | `false` | no |
| <a name="input_environment"></a> [environment](#input\_environment) | The environment (e.g., staging, production). | `string` | n/a | yes |
| <a name="input_kms_key_arn"></a> [kms\_key\_arn](#input\_kms\_key\_arn) | The ARN of the KMS key. | `string` | n/a | yes |
| <a name="input_project_name"></a> [project\_name](#input\_project\_name) | The name of the project. | `string` | n/a | yes |
| <a name="input_proxy_security_group_ids"></a> [proxy\_security\_group\_ids](#input\_proxy\_security\_group\_ids) | A list of security group IDs to associate with the RDS proxy. | `list(string)` | `[]` | no |
| <a name="input_secret_recovery_window_in_days"></a> [secret\_recovery\_window\_in\_days](#input\_secret\_recovery\_window\_in\_days) | The number of days that Secrets Manager waits before it can delete the secret. Set to 0 to delete immediately. | `number` | `7` | no |
| <a name="input_security_group_ids"></a> [security\_group\_ids](#input\_security\_group\_ids) | A list of security group IDs to associate with the RDS database. | `list(string)` | n/a | yes |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_db_password_arn"></a> [db\_password\_arn](#output\_db\_password\_arn) | The SSM Parameter ARN of password of the RDS database. |
| <a name="output_db_proxy_endpoint"></a> [db\_proxy\_endpoint](#output\_db\_proxy\_endpoint) | The endpoint of the RDS proxy. |
<!-- END_TF_DOCS -->
