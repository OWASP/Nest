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

## Resources

| Name | Type |
| ---- | ---- |
| [aws_acm_certificate.main](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/acm_certificate) | resource |
| [aws_acm_certificate_validation.main](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/acm_certificate_validation) | resource |
| [aws_lb.main](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb) | resource |
| [aws_lb_listener.http_redirect](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb_listener) | resource |
| [aws_lb_listener.https](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb_listener) | resource |
| [aws_lb_listener_rule.backend_https](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb_listener_rule) | resource |
| [aws_lb_target_group.backend](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb_target_group) | resource |
| [aws_lb_target_group.frontend](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb_target_group) | resource |
| [aws_s3_bucket.alb_logs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket) | resource |
| [aws_s3_bucket_lifecycle_configuration.alb_logs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_lifecycle_configuration) | resource |
| [aws_s3_bucket_policy.alb_logs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_policy) | resource |
| [aws_s3_bucket_public_access_block.alb_logs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_public_access_block) | resource |
| [aws_s3_bucket_server_side_encryption_configuration.alb_logs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_server_side_encryption_configuration) | resource |
| [aws_s3_bucket_versioning.alb_logs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_versioning) | resource |
| [random_id.suffix](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/id) | resource |
| [aws_elb_service_account.main](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/elb_service_account) | data source |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_alb_sg_id"></a> [alb\_sg\_id](#input\_alb\_sg\_id) | The security group ID for the ALB. | `string` | n/a | yes |
| <a name="input_backend_health_check_path"></a> [backend\_health\_check\_path](#input\_backend\_health\_check\_path) | The health check path for the backend target group. | `string` | `"/status/"` | no |
| <a name="input_backend_port"></a> [backend\_port](#input\_backend\_port) | The port for the backend target group. | `number` | `8000` | no |
| <a name="input_common_tags"></a> [common\_tags](#input\_common\_tags) | A map of common tags to apply to all resources. | `map(string)` | `{}` | no |
| <a name="input_domain_name"></a> [domain\_name](#input\_domain\_name) | The domain name for ACM certificate (e.g., nest.owasp.dev). | `string` | n/a | yes |
| <a name="input_environment"></a> [environment](#input\_environment) | The environment name (e.g., staging, production). | `string` | n/a | yes |
| <a name="input_frontend_health_check_path"></a> [frontend\_health\_check\_path](#input\_frontend\_health\_check\_path) | The health check path for the frontend target group. | `string` | `"/api/health"` | no |
| <a name="input_frontend_port"></a> [frontend\_port](#input\_frontend\_port) | The port for the frontend target group. | `number` | `3000` | no |
| <a name="input_log_retention_days"></a> [log\_retention\_days](#input\_log\_retention\_days) | The number of days to retain ALB access logs. | `number` | `90` | no |
| <a name="input_project_name"></a> [project\_name](#input\_project\_name) | The name of the project. | `string` | n/a | yes |
| <a name="input_public_subnet_ids"></a> [public\_subnet\_ids](#input\_public\_subnet\_ids) | A list of public subnet IDs for the ALB. | `list(string)` | n/a | yes |
| <a name="input_static_s3_bucket_name"></a> [static\_s3\_bucket\_name](#input\_static\_s3\_bucket\_name) | S3 static assets bucket name. | `string` | n/a | yes |
| <a name="input_vpc_id"></a> [vpc\_id](#input\_vpc\_id) | The ID of the VPC. | `string` | n/a | yes |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_acm_certificate_arn"></a> [acm\_certificate\_arn](#output\_acm\_certificate\_arn) | The ARN of the ACM certificate. |
| <a name="output_acm_certificate_domain_validation_options"></a> [acm\_certificate\_domain\_validation\_options](#output\_acm\_certificate\_domain\_validation\_options) | The domain validation options for ACM certificate DNS validation. |
| <a name="output_acm_certificate_status"></a> [acm\_certificate\_status](#output\_acm\_certificate\_status) | The status of the ACM certificate. |
| <a name="output_alb_arn"></a> [alb\_arn](#output\_alb\_arn) | The ARN of the ALB. |
| <a name="output_alb_dns_name"></a> [alb\_dns\_name](#output\_alb\_dns\_name) | The DNS name of the ALB. |
| <a name="output_alb_zone_id"></a> [alb\_zone\_id](#output\_alb\_zone\_id) | The zone ID of the ALB. |
| <a name="output_backend_target_group_arn"></a> [backend\_target\_group\_arn](#output\_backend\_target\_group\_arn) | The ARN of the backend target group. |
| <a name="output_frontend_target_group_arn"></a> [frontend\_target\_group\_arn](#output\_frontend\_target\_group\_arn) | The ARN of the frontend target group. |
| <a name="output_http_listener_arn"></a> [http\_listener\_arn](#output\_http\_listener\_arn) | The ARN of the HTTP listener. |
| <a name="output_https_listener_arn"></a> [https\_listener\_arn](#output\_https\_listener\_arn) | The ARN of the HTTPS listener. |
<!-- END_TF_DOCS -->
