# Infrastructure

This document provides instructions on how to setup the infrastructure for this project.

## Prerequisites

Ensure you have the following setup/installed:

- Setup Project: [CONTRIBUTING.md](https://github.com/OWASP/Nest/blob/main/CONTRIBUTING.md)
- Terraform: [Terraform Documentation](https://developer.hashicorp.com/terraform/docs)
- AWS CLI: [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- An AWS account with credentials configured locally.

## Setting up the infrastructure

Follow these steps to set up the infrastructure:

1. **Change the Directory**:

   - Change the directory using the following command:

     ```bash
     cd infrastructure/
     ```

    *Note*: The following steps assume the current working directory is `infrastructure/`

2. **Create Variables File**:

   - Create a local variables file in the `infrastructure` directory:

     ```bash
     touch terraform.tfvars
     ```

   - Copy the contents from the template file into your new local environment file:

     ```bash
     cat terraform.tfvars.example > terraform.tfvars
     ```

3. **Apply Changes**:

   - Init terraform if needed:

     ```bash
     terraform init
     ```

   - Apply the changes and create the infrastructure using the following command:

     ```bash
     terraform apply
     ```

4. **Populate Secrets**:

   - Visit the AWS Console > Systems Manager > Parameter Store.
   - Populate all `DJANGO_*` secrets that have `to-be-set-in-aws-console` value.


## Setting up Zappa

The Django backend deployment is managed by Zappa. This includes the API Gateway, IAM roles, and Lambda Function provision.

1. **Change Directory**:

   - Change the directory to `backend/` using the following command:

     ```bash
     cd ../backend/
     ```

    *Note*: The following steps assume the current working directory is `backend/`

2. **Setup Dependencies**:

   - This step may differ for different operating systems.
   - The goal is to install dependencies listed in `pyproject.toml`.
   - Steps for Linux:

     ```bash
     poetry install && eval $(poetry env activate)
     ```

3. **Create Zappa Settings File**:

- Create a local Zappa settings file in the `backend` directory:

     ```bash
     touch zappa_settings.json
     ```

- Copy the contents from the template file into your new local environment file:

     ```bash
     cat zappa_settings.example.json > zappa_settings.json
     ```

4. **Populate Settings File**:

- Replace all `${...}` variables in `zappa_settings.json` with appropriate output variables.

5. **Deploy**:

    - *Note*: Make sure to populate all `DJANGO_*` secrets that are set as `to-be-set-in-aws-console`
      in the Parameter Store. The deployment might fail with no logs if secrets such as
      `DJANGO_SLACK_BOT_TOKEN` are invalid.

    ```bash
    zappa deploy staging
    ```

Once deployed, use the URL provided by Zappa to test the API.

## Setup Database

Migrate and load data into the new database.

1. **Setup ECR Image**:
   - Login to the Elastic Container Registry using the following command:

     *Note*: replace `us-east-2` with configured region and `000000000000` with AWS Account ID.

     *Warning*: Configure a credential helper instead of using following command to login.

     ```bash
     aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 000000000000.dkr.ecr.us-east-2.amazonaws.com
     ```

   - Build the backend image using the following command:

     ```bash
     docker build -t owasp-nest-staging-backend:latest -f docker/Dockerfile .
     ```

   - Tag the image:
     *Note*: replace `us-east-2` with configured region and `000000000000` with AWS Account ID.

     ```bash
      docker tag owasp-nest-staging-backend:latest 000000000000.dkr.ecr.us-east-2.amazonaws.com/owasp-nest-staging-backend:latest
     ```

   - Push the image:
     *Note*: replace `us-east-2` with configured region and `000000000000` with AWS Account ID.

     ```bash
      docker push 000000000000.dkr.ecr.us-east-2.amazonaws.com/owasp-nest-staging-backend:latest
     ```

2. **Upload Fixture to S3**:
   - Upload the fixture present in `backend/data` to `nest-fixtures` bucket using the following command:

     ```bash
     aws s3 cp data/nest.json.gz s3://nest-fixtures/
     ```

3. **Run ECS Tasks**:
   - Head over to Elastic Container Service in the AWS Console.
   - Click on `owasp-nest-staging-migrate` in `Task Definitions` section.
   - Select the task definition revision.
   - Click Deploy > Run Task.
   - Use the following configuration:
      - Networking:
         - VPC: owasp-nest-staging-vpc
         - Subnets: subnets will be auto-selected due to VPC selection.
         - Security group name: select all with `owasp-nest-staging-` prefix.
            (*Note*: temporary step, will be further improved)
   - Click "Create"
   - The task is now running... Click on the task ID to view Logs, Status, etc.
   - Follow the same steps for `owasp-nest-staging-load-data` and `owasp-nest-staging-index-data`.

## Cleaning Up

- To delete the deployment use the following command:

  ```bash
  zappa undeploy staging
  ```

- To destroy Terraform infrastructure:

  ```bash
  terraform destroy
  ```

## Helpful Commands

- To view logs for a `staging` deployment run:

  ```bash
  zappa tail staging
  ```

- To update a Zappa `staging` deployment run:

  ```bash
  zappa update staging
  ```
