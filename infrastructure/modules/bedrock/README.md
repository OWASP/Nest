# Bedrock

Creates an invocation policy scoped to one foundation model or inference profile.
For profiles, destination models can only be invoked through the selected profile.
The caller attaches the policy to the application task role.

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
| [aws_iam_policy.main](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_bedrock_foundation_model.main](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/bedrock_foundation_model) | data source |
| [aws_bedrock_inference_profile.main](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/bedrock_inference_profile) | data source |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_common_tags"></a> [common\_tags](#input\_common\_tags) | A map of common tags to apply to all resources. | `map(string)` | `{}` | no |
| <a name="input_model_name"></a> [model\_name](#input\_model\_name) | Approved Bedrock foundation model or inference profile ID. | `string` | n/a | yes |
| <a name="input_name_prefix"></a> [name\_prefix](#input\_name\_prefix) | Name prefix for the Bedrock invocation policy. | `string` | n/a | yes |
| <a name="input_target_type"></a> [target\_type](#input\_target\_type) | Type of the approved Bedrock target: foundation-model or inference-profile. | `string` | `"foundation-model"` | no |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_policy_arn"></a> [policy\_arn](#output\_policy\_arn) | ARN of the policy allowing invocation of the selected Bedrock target. |
<!-- END_TF_DOCS -->
