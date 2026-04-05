# Parameters

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | ~> 1.14.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 6.36.0 |
| <a name="requirement_random"></a> [random](#requirement\_random) | ~> 3.8.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | 6.36.0 |
| <a name="provider_random"></a> [random](#provider\_random) | 3.8.1 |

## Resources

| Name | Type |
|------|------|
| [aws_ssm_parameter.django_algolia_application_id](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.django_algolia_write_api_key](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.django_allowed_hosts](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.django_allowed_origins](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.django_aws_storage_bucket_name](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.django_configuration](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.django_db_host](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.django_db_name](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.django_db_port](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.django_db_user](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.django_github_app_id](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.django_github_app_installation_id](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.django_open_ai_secret_key](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.django_redis_host](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.django_redis_use_tls](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.django_release_version](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.django_secret_key](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.django_sentry_dsn](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.django_settings_module](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.django_slack_bot_token](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.django_slack_signing_secret](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.github_token](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.nest_github_app_private_key](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.next_server_csrf_url](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.next_server_disable_ssr](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.next_server_github_client_id](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.next_server_github_client_secret](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.next_server_graphql_url](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.nextauth_secret](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.nextauth_url](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.slack_bot_token](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [random_string.django_secret_key](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/string) | resource |
| [random_string.nextauth_secret](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/string) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_common_tags"></a> [common\_tags](#input\_common\_tags) | A map of common tags to apply to all resources. | `map(string)` | `{}` | no |
| <a name="input_db_password_arn"></a> [db\_password\_arn](#input\_db\_password\_arn) | The SSM Parameter ARN of password of the database. | `string` | n/a | yes |
| <a name="input_django_allowed_hosts"></a> [django\_allowed\_hosts](#input\_django\_allowed\_hosts) | Django allowed hosts - hostname only, no protocol (e.g., nest.owasp.dev). | `string` | n/a | yes |
| <a name="input_django_allowed_origins"></a> [django\_allowed\_origins](#input\_django\_allowed\_origins) | The Django allowed CORS origins (comma-separated URLs with protocol). | `string` | n/a | yes |
| <a name="input_django_aws_static_bucket_name"></a> [django\_aws\_static\_bucket\_name](#input\_django\_aws\_static\_bucket\_name) | The name of the S3 bucket for Django static files. | `string` | n/a | yes |
| <a name="input_django_configuration"></a> [django\_configuration](#input\_django\_configuration) | The name of the Django configuration to use (e.g., Staging, Production). | `string` | n/a | yes |
| <a name="input_django_db_host"></a> [django\_db\_host](#input\_django\_db\_host) | The hostname of the database. | `string` | n/a | yes |
| <a name="input_django_db_name"></a> [django\_db\_name](#input\_django\_db\_name) | The name of the database. | `string` | n/a | yes |
| <a name="input_django_db_port"></a> [django\_db\_port](#input\_django\_db\_port) | The port of the database. | `string` | n/a | yes |
| <a name="input_django_db_user"></a> [django\_db\_user](#input\_django\_db\_user) | The user for the database. | `string` | n/a | yes |
| <a name="input_django_redis_host"></a> [django\_redis\_host](#input\_django\_redis\_host) | The hostname of the Redis cache. | `string` | n/a | yes |
| <a name="input_django_redis_use_tls"></a> [django\_redis\_use\_tls](#input\_django\_redis\_use\_tls) | Whether Redis connections should use TLS (required for ElastiCache with transit encryption). | `bool` | `true` | no |
| <a name="input_django_release_version"></a> [django\_release\_version](#input\_django\_release\_version) | The Django release version. | `string` | n/a | yes |
| <a name="input_django_settings_module"></a> [django\_settings\_module](#input\_django\_settings\_module) | The location of the Django settings module to use (e.g., settings.staging, settings.production). | `string` | n/a | yes |
| <a name="input_enable_additional_parameters"></a> [enable\_additional\_parameters](#input\_enable\_additional\_parameters) | Whether to create additional parameters (e.g. for production). | `bool` | `false` | no |
| <a name="input_environment"></a> [environment](#input\_environment) | The environment (e.g., staging, production). | `string` | n/a | yes |
| <a name="input_next_server_csrf_url"></a> [next\_server\_csrf\_url](#input\_next\_server\_csrf\_url) | The server-side CSRF URL for Next.js SSR (e.g., https://nest.owasp.dev/csrf/). | `string` | n/a | yes |
| <a name="input_next_server_graphql_url"></a> [next\_server\_graphql\_url](#input\_next\_server\_graphql\_url) | The server-side GraphQL URL for Next.js SSR (e.g., https://nest.owasp.dev/graphql/). | `string` | n/a | yes |
| <a name="input_nextauth_url"></a> [nextauth\_url](#input\_nextauth\_url) | The NextAuth base URL (frontend URL with protocol). | `string` | n/a | yes |
| <a name="input_project_name"></a> [project\_name](#input\_project\_name) | The name of the project. | `string` | n/a | yes |
| <a name="input_redis_password_arn"></a> [redis\_password\_arn](#input\_redis\_password\_arn) | The SSM Parameter ARN of password of the Redis cache. | `string` | n/a | yes |
| <a name="input_slack_bot_token_suffix"></a> [slack\_bot\_token\_suffix](#input\_slack\_bot\_token\_suffix) | The Suffix for the Slack bot token. | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_django_ssm_parameter_arns"></a> [django\_ssm\_parameter\_arns](#output\_django\_ssm\_parameter\_arns) | Map of environment variable names to the ARNs of all SSM parameters (Required by Django). |
| <a name="output_frontend_ssm_parameter_arns"></a> [frontend\_ssm\_parameter\_arns](#output\_frontend\_ssm\_parameter\_arns) | Map of frontend environment variable names to the ARNs of all SSM parameters. |
<!-- END_TF_DOCS -->

