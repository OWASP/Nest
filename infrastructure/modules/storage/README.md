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

| Name | Source | Version |
| ---- | ------ | ------- |
| <a name="module_fixtures_bucket"></a> [fixtures\_bucket](#module\_fixtures\_bucket) | ./modules/s3-bucket | n/a |
| <a name="module_shared_data_bucket"></a> [shared\_data\_bucket](#module\_shared\_data\_bucket) | ./modules/shared-data-bucket | n/a |
| <a name="module_static_bucket"></a> [static\_bucket](#module\_static\_bucket) | ./modules/s3-bucket | n/a |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_common_tags"></a> [common\_tags](#input\_common\_tags) | A map of common tags to apply to all resources. | `map(string)` | `{}` | no |
| <a name="input_environment"></a> [environment](#input\_environment) | The environment (e.g., staging, production). | `string` | n/a | yes |
| <a name="input_fixtures_bucket_name"></a> [fixtures\_bucket\_name](#input\_fixtures\_bucket\_name) | The name of the S3 bucket for fixtures. | `string` | n/a | yes |
| <a name="input_kms_key_arn"></a> [kms\_key\_arn](#input\_kms\_key\_arn) | The ARN of the KMS key (used for fixtures bucket encryption). | `string` | n/a | yes |
| <a name="input_project_name"></a> [project\_name](#input\_project\_name) | The name of the project. | `string` | n/a | yes |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_fixtures_read_only_policy_arn"></a> [fixtures\_read\_only\_policy\_arn](#output\_fixtures\_read\_only\_policy\_arn) | The ARN of the fixtures read-only IAM policy. |
| <a name="output_fixtures_s3_bucket_arn"></a> [fixtures\_s3\_bucket\_arn](#output\_fixtures\_s3\_bucket\_arn) | The ARN of the S3 bucket for fixtures. |
| <a name="output_fixtures_s3_bucket_name"></a> [fixtures\_s3\_bucket\_name](#output\_fixtures\_s3\_bucket\_name) | The name of the S3 bucket for fixtures. |
| <a name="output_shared_data_bucket_name"></a> [shared\_data\_bucket\_name](#output\_shared\_data\_bucket\_name) | The name of the global shared public data S3 bucket (e.g. nest.dump). |
| <a name="output_static_read_write_policy_arn"></a> [static\_read\_write\_policy\_arn](#output\_static\_read\_write\_policy\_arn) | The ARN of the static files read/write IAM policy. |
| <a name="output_static_s3_bucket_name"></a> [static\_s3\_bucket\_name](#output\_static\_s3\_bucket\_name) | The name of the S3 bucket for static files. |
<!-- END_TF_DOCS -->
