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

1. **Setup Backend (one-time setup)**:

  - Navigate to the backend directory:

    ```bash
    cd infrastructure/backend/
    ```

  > [!NOTE]
  > Optionally change the region: set `aws_region` in a `.tfvars` file.

  - Initialize Terraform if needed:

    ```bash
    terraform init
    ```

  - Apply the changes to create the backend resources:

    ```bash
    terraform apply
    ```

  > [!NOTE]
  > Copy the state bucket name from the output.

  > [!NOTE]
  > It is recommended to not destroy the backend resources unless absolutely necessary.

2. **Setup Main Infrastructure (staging)**:

  - Navigate to the main infrastructure directory. If you are in `infrastructure/backend`, you can use:

    ```bash
    cd ../staging/
    ```

  - Create a local variables file:

    ```bash
    touch terraform.tfvars
    ```

  - Copy the contents from the example file:

    ```bash
    cat terraform.tfvars.example > terraform.tfvars
    ```

  - Create a local backend configuration file:

    ```bash
    touch terraform.tfbackend
    ```

  - Copy the contents from the example file:

    ```bash
    cat terraform.tfbackend.example > terraform.tfbackend
    ```

  > [!NOTE]
  > Update the state bucket name in `terraform.tfbackend` with the name of the state bucket created in the previous step.

  > [!NOTE]
  > Update defaults (e.g. `region`) as needed.

  - Initialize Terraform with the backend configuration:

    ```bash
    terraform init -backend-config=terraform.tfbackend
    ```

  - Apply the changes to create the main infrastructure using the command:

    ```bash
    terraform apply
    ```

3. **Populate Secrets**

  - Visit the AWS Console > Systems Manager > Parameter Store.
  - Populate all `DJANGO_*` secrets that have `to-be-set-in-aws-console` value.

## Setting up Zappa

The Django backend deployment is managed by Zappa. This includes the API Gateway, IAM roles, and Lambda Function provision.

1. **Change Directory**:

  - Change the directory to `backend/` using the following command:

    ```bash
    cd ../../backend/
    ```

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

  > [!NOTE]
  > Make sure to populate all `DJANGO_*` secrets that are set as `to-be-set-in-aws-console` in the Parameter Store. The deployment might fail with no logs if secrets such as `DJANGO_SLACK_BOT_TOKEN` are invalid.

  ```bash
  zappa deploy staging
  ```

  > [!NOTE]
  > If the deployment is successful but returns a `5xx` error, resolve the issues and use `zappa undeploy staging` & `zappa deploy staging`. The command `zappa update staging` may not work.

  Once deployed, use the URL provided by Zappa to test the API.

## Populate ECR Repositories
ECR Repositories are used to store images used by ECS (Frontend + Backend Tasks)

1. **Login to ECR**:

  - Login to the Elastic Container Registry using the following command:

    > [!NOTE]
    > Replace `us-east-2` with configured region and `000000000000` with AWS Account ID.

    > [!WARNING]
    > Configure a credential helper instead of using following command to login.

    ```bash
    aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 000000000000.dkr.ecr.us-east-2.amazonaws.com
    ```

2. **Uplaod backend image to ECR**:

  - Build the backend image using the following command:

    ```bash
    docker build -t owasp-nest-staging-backend:latest -f docker/backend/Dockerfile backend/
    ```

  - Tag the image:

    > [!NOTE]
    > Replace `us-east-2` with configured region and `000000000000` with AWS Account ID.

    ```bash
    docker tag owasp-nest-staging-backend:latest 000000000000.dkr.ecr.us-east-2.amazonaws.com/owasp-nest-staging-backend:latest
    ```

  - Push the image:

    > [!NOTE]
    > Replace `us-east-2` with configured region and `000000000000` with AWS Account ID.

    ```bash
    docker push 000000000000.dkr.ecr.us-east-2.amazonaws.com/owasp-nest-staging-backend:latest
    ```

3. **Uplaod frontend image to ECR**:

  - Build the frontend image using the following command:

    > [!NOTE]
    > Make sure to update the frontend `.env` file with correct `NEXT_PUBLIC_*` variables.
    > These are injected at build time.

    ```bash
    docker build -t owasp-nest-staging-frontend:latest -f docker/frontend/Dockerfile frontend/
    ```

  - Tag the image:

    > [!NOTE]
    > Replace `us-east-2` with configured region and `000000000000` with AWS Account ID.

    ```bash
    docker tag owasp-nest-staging-frontend:latest 000000000000.dkr.ecr.us-east-2.amazonaws.com/owasp-nest-staging-frontend:latest
    ```

  - Push the image:

    > [!NOTE]
    > Replace `us-east-2` with configured region and `000000000000` with AWS Account ID.

    ```bash
    docker push 000000000000.dkr.ecr.us-east-2.amazonaws.com/owasp-nest-staging-frontend:latest
    ```

## Setup Database
Migrate and load data into the new database.

1. **Upload Fixture to S3**:

  - Upload the fixture present in `backend/data` to `nest-fixtures` bucket using the following command:

    ```bash
    aws s3 cp data/nest.json.gz s3://owasp-nest-fixtures-<id>/
    ```

2. **Run ECS Tasks**:

  - Head over to Elastic Container Service in the AWS Console.
  - Click on `owasp-nest-staging-migrate` in `Task Definitions` section.
  - Select the task definition revision.
  - Click Deploy > Run Task.
  - Use the following configuration:
    - Environment: Cluster: owasp-nest-staging-tasks-cluster
    - Networking:
      - VPC: owasp-nest-staging-vpc
      - Subnets: subnets will be auto-selected due to VPC selection.
      - Security group name: select the ECS security group (e.g. `owasp-nest-staging-ecs-sg`).
  - Click "Create"
  - The task is now running... Click on the task ID to view Logs, Status, etc.
  - Follow the same steps for `owasp-nest-staging-load-data` and `owasp-nest-staging-index-data`.

## Configure Domain and Frontend

1. **Validate ACM Certificate**:

  - Get the DNS validation records:

    ```bash
    terraform output acm_certificate_domain_validation_options
    ```

  - Add the CNAME records to your DNS provider.

  - Wait some time and run `terraform apply` to check if the certificate status has changed to `ISSUED`:

    ```bash
    terraform apply
    ```

  - Add a CNAME record and point the domain to the frontend ALB.

2. **Configure Frontend Parameters**:

  - Update the frontend server (`NEXT_SERVER_*`) parameters using the Lambda URL from Terraform outputs.

3. **Restart Frontend ECS Tasks**:

  - Force a new deployment to pick up the updated configuration:

    > [!NOTE]
    > Replace `us-east-2` with configured region.

    ```bash
    aws ecs update-service \
        --cluster owasp-nest-staging-frontend-cluster \
        --service owasp-nest-staging-frontend-service \
        --force-new-deployment \
        --region us-east-2
    ```

## Cleaning Up

- To delete the deployment use the following command:

  ```bash
  zappa undeploy staging
  ```

- Ensure all buckets and ECR repositories are empty.

> [!NOTE]
> Some resources have `prevent_destroy` set to `true`. Please set it to `false` before destruction.

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
