# Runtime secrets LocalStack fixture

This fixture tests the runtime-secrets migration without creating a complete Nest environment. It requires an already-running LocalStack instance plus `tflocal`, `awslocal`, AWS CLI, and `jq`.

Run it from the repository root:

```bash
bash infrastructure/localstack/test.sh
```

The test applies `prepare`, confirms legacy secret-valued SSM parameters and new Secrets Manager containers coexist, populates external secrets with fake values, and runs the deployment preflight. It then applies `complete` to the same state and verifies that secret-valued SSM parameters disappear while non-secret parameters remain. Finally, it inspects ECS `valueFrom` references and the execution-role IAM policy before destroying the fixture.

The script does not start LocalStack or manage its authentication token.
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

| Name | Source | Version |
| ---- | ------ | ------- |
| <a name="module_parameters"></a> [parameters](#module\_parameters) | ../modules/parameters | n/a |

## Resources

| Name | Type |
| ---- | ---- |
| [aws_ecs_task_definition.django](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ecs_task_definition) | resource |
| [aws_iam_policy.runtime_secrets](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_role.ecs_execution](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy_attachment.runtime_secrets](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_kms_key.main](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key) | resource |
| [aws_secretsmanager_secret.db](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret) | resource |
| [aws_secretsmanager_secret.redis](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret) | resource |
| [aws_secretsmanager_secret_version.db](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret_version) | resource |
| [aws_secretsmanager_secret_version.redis](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret_version) | resource |
| [aws_ssm_parameter.db_password](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.redis_password](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_runtime_secrets_mode"></a> [runtime\_secrets\_mode](#input\_runtime\_secrets\_mode) | n/a | `string` | `"prepare"` | no |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_django_value_from"></a> [django\_value\_from](#output\_django\_value\_from) | Django environment variable names mapped to ECS valueFrom references. |
| <a name="output_execution_policy_arn"></a> [execution\_policy\_arn](#output\_execution\_policy\_arn) | ARN of the fixture execution-role policy. |
| <a name="output_frontend_value_from"></a> [frontend\_value\_from](#output\_frontend\_value\_from) | Frontend environment variable names mapped to ECS valueFrom references. |
| <a name="output_kms_key_arn"></a> [kms\_key\_arn](#output\_kms\_key\_arn) | ARN of the fixture KMS key. |
| <a name="output_secretsmanager_secret_arns"></a> [secretsmanager\_secret\_arns](#output\_secretsmanager\_secret\_arns) | Bare Secrets Manager ARNs passed to the execution-role policy. |
| <a name="output_task_definition_arn"></a> [task\_definition\_arn](#output\_task\_definition\_arn) | ARN of the fixture Django ECS task definition. |
<!-- END_TF_DOCS -->