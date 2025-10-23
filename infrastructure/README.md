# Infrastructure

This document provides instructions on how to setup the infrastructure for this project.

## Prerequisites
Ensure you have the following setup/installed:

- Setup Project: [CONTRIBUTING.md](https://github.com/OWASP/Nest/blob/main/CONTRIBUTING.md)
- Terraform: [Terraform Documentation](https://developer.hashicorp.com/terraform/docs)
- An AWS account with credentials configured locally.

## Setting up the infrastructure
Follow these steps to set up the infrastructure:

1. **Change the Directory**:

   - Change the directory using the following command:

     ```bash
     cd infrastructure/
     ```

*Note*: The following steps assume the current working directory is `infrastructure/`

You can override the default values by creating a `terraform.tfvars` file in the `infrastructure/` directory.

# TODO: Provide an example terraform.tfvars with important vars


## Setting up Zappa Deployment

The Django backend deployment is managed by Zappa. This includes the API Gateway, IAM roles, and Lambda Function provision.

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
