# Infrastructure

This document provides instructions on how to manage the infrastructure for this project using Terraform and Zappa.

## Terraform

### Prerequisites

- Terraform
- An AWS account with credentials configured locally.

### Usage

1.  **Initialize Terraform:**

    ```bash
    terraform init
    ```

2.  **Plan the changes:**

    ```bash
    terraform plan
    ```

3.  **Apply the changes:**

    ```bash
    terraform apply
    ```

### Variables

You can override the default values by creating a `terraform.tfvars` file in the `infrastructure/` directory.

# TODO: Provide an example terraform.tfvars with important vars


### Outputs

Get the output values using the `terraform output` command. These outputs will be used for Zappa configuration.


```bash
terraform output
```

```bash
terraform output -raw db_password redis_auth_token
```

## Zappa Deployment

The Django backend deployment is managed by Zappa, this also includes the API Gateway, IAM roles, and Lambda Function provision.

### Install poetry dependencies

1.  **Install dependencies using Poetry:**

    ```bash
    poetry install
    ```

2.  **Activate the virtual environment:**

    ```bash
    eval $(poetry env activate)
    ```

3.  **Create a `zappa_settings.json` file:**

    ```bash
    cp zappa_settings.example.json zappa_settings.json
    ```

Replace all variables in the copied `zappa_settings.json` with appropriate secrets.
# TODO: explain this step

4.  **Deploy staging:**

    ```bash
    zappa deploy staging
    ```

Once deployed, Zappa will provide you with a URL. You can use this URL to test the API.

### Updating
After making necessary changes, you may run the following command to update the deployment.
```bash
zappa update staging
```

### Cleaning Up

To delete the deployment, you can use the following command:

```bash
zappa undeploy local
```

Then run this command to destroy the terraform infrastructure:

```bash
terraform destroy
```
