# Infrastructure

This document provides instructions on how to setup the infrastructure for this project.

## Prerequisites

Ensure you have the following setup/installed:

- Setup Project: [CONTRIBUTING.md](https://github.com/OWASP/Nest/blob/main/CONTRIBUTING.md)
- Terraform: [Terraform Documentation](https://developer.hashicorp.com/terraform/docs)
- AWS CLI: [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- An AWS account.
Note: Refer to the respective `README.md` files for more information.

## Setting up the infrastructure

Follow these steps to set up the infrastructure:

1. **Setup Backend (one-time setup)**:

- Prerequisite: Create a `nest-backend` IAM user with the policies defined in `infrastructure/backend/README.md`.

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
  > It is recommended to not destroy the backend resources unless absolutely necessary.

1. **Bootstrap IAM Role**:

- Prerequisite: Create a `nest-bootstrap` IAM user with the policies defined in `infrastructure/bootstrap/README.md`.

- Navigate to the bootstrap directory:

    ```bash
    cd infrastructure/bootstrap/
    ```

- Copy the contents from the template file into your new local terraform variables file:

    ```bash
    cp terraform.tfvars.example terraform.tfvars
    ```

- Copy the contents from the template file into your new terraform backend file:

    ```bash
    cp terraform.tfbackend.example terraform.tfbackend
    ```

  > [!NOTE]
  > Update the state bucket name in `terraform.tfbackend` with the name of the state bucket (bootstrap) created in the previous step.

- Initialize Terraform if needed:

    ```bash
    terraform init -backend-config=terraform.tfbackend
    ```

- Apply the changes to create the bootstrap resources:

    ```bash
    terraform apply
    ```

1. **Setup Main Infrastructure (staging)**:

- Prerequisite: Create a `nest-staging` IAM user with the policies defined in `infrastructure/staging/README.md`

- Navigate to the main infrastructure directory. If you are in `infrastructure/backend`, you can use:

    ```bash
    cd infrastructure/staging/
    ```

- Copy the contents from the template file into your new local terraform variables file:

    ```bash
    cp terraform.tfvars.example terraform.tfvars
    ```

- Copy the contents from the template file into your new local terraform backend file:

    ```bash
    cp terraform.tfbackend.example terraform.tfbackend
    ```

  > [!NOTE]
  > Update the state bucket name in `terraform.tfbackend` with the name of the state bucket created in the previous step.
  > Update defaults (e.g. `region`) as needed.

- Initialize Terraform with the backend configuration:

    ```bash
    terraform init -backend-config=terraform.tfbackend
    ```

- Apply the changes to create the main infrastructure using the command:

    ```bash
    terraform apply
    ```

1. **Populate Secrets**

- Visit the AWS Console > Systems Manager > Parameter Store.
- Populate all `DJANGO_*` secrets that have `to-be-set-in-aws-console` value.

## Setting up Zappa

The Django backend deployment is managed by Zappa. This includes the IAM roles, and Lambda Function provision.

1. **Change Directory**:

- Change the directory to `backend/` using the following command:

    ```bash
    cd backend/
    ```

1. **Setup Dependencies**:

- This step may differ for different operating systems.
- The goal is to install dependencies listed in `pyproject.toml`.
- Steps for Linux:

    ```bash
    poetry sync --without test --without video && eval $(poetry env activate)
    ```

1. **Create Zappa Settings File**:

- Copy the contents from the template file into your new local Zappa settings file:

    ```bash
    cp zappa_settings.template.json zappa_settings.json
    ```

1. **Populate Settings File**:

- Replace all `${...}` variables in `zappa_settings.json` with appropriate output variables.

1. **Deploy**:

  > [!NOTE]
  > Make sure to populate all `DJANGO_*` secrets that are set as `to-be-set-in-aws-console` in the Parameter Store. The deployment might fail with no logs if secrets such as `DJANGO_SLACK_BOT_TOKEN` are invalid.

  ```bash
  zappa deploy staging
  ```

  > [!NOTE]
  > If the deployment is successful but returns a `5xx` error, resolve the issues and use `zappa undeploy staging` & `zappa deploy staging`. The command `zappa update staging` may not work.

1. **Configure ALB Routing**:

- Run `zappa status staging` to get Zappa details.
- Update `staging`'s `terraform.tfvars` with the Lambda details:

    ```hcl
    lambda_function_name = "nest-staging"
    ```

- Apply the changes to create ALB routing:

    ```bash
    terraform apply
    ```

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

1. **Upload backend image to ECR**:

- Build the backend image using the following command:

    ```bash
    docker build -t nest-staging-backend:latest -f docker/backend/Dockerfile backend/
    ```

- Tag the image:

    > [!NOTE]
    > Replace `us-east-2` with configured region and `000000000000` with AWS Account ID.

    ```bash
    docker tag nest-staging-backend:latest 000000000000.dkr.ecr.us-east-2.amazonaws.com/nest-staging-backend:latest
    ```

- Push the image:

    > [!NOTE]
    > Replace `us-east-2` with configured region and `000000000000` with AWS Account ID.

    ```bash
    docker push 000000000000.dkr.ecr.us-east-2.amazonaws.com/nest-staging-backend:latest
    ```

1. **Upload frontend image to ECR**:

- Build the frontend image using the following command:

    > [!NOTE]
    > Make sure to update the frontend `.env` file with correct `NEXT_PUBLIC_*` variables.
    > These are injected at build time.

    ```bash
    docker build -t nest-staging-frontend:latest -f docker/frontend/Dockerfile frontend/
    ```

- Tag the image:

    > [!NOTE]
    > Replace `us-east-2` with configured region and `000000000000` with AWS Account ID.

    ```bash
    docker tag nest-staging-frontend:latest 000000000000.dkr.ecr.us-east-2.amazonaws.com/nest-staging-frontend:latest
    ```

- Push the image:

    > [!NOTE]
    > Replace `us-east-2` with configured region and `000000000000` with AWS Account ID.

    ```bash
    docker push 000000000000.dkr.ecr.us-east-2.amazonaws.com/nest-staging-frontend:latest
    ```

## Setup Database

Migrate and load data into the new database.

1. **Upload Fixture to S3**:

- Upload the fixture present in `backend/data` to `nest-fixtures` bucket using the following command:

    ```bash
    aws s3 cp backend/data/nest.dump s3://nest-fixtures-<RANDOM_ID>/
    ```

1. **Run ECS Tasks**:

- Head over to Elastic Container Service in the AWS Console.
- Click on `nest-staging-migrate` in `Task Definitions` section.
- Select the task definition revision.
- Click Deploy > Run Task.
- Use the following configuration:
  - Environment: Cluster: nest-staging-tasks-cluster
  - Networking:
    - VPC: nest-staging-vpc
    - Subnets: subnets will be auto-selected due to VPC selection.
    - Security group name: select the ECS security group (e.g. `nest-staging-ecs-sg`).
- Click "Create"
- The task is now running... Click on the task ID to view Logs, Status, etc.
- Follow the same steps for `nest-staging-load-data` and `nest-staging-index-data`.

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

1. **Configure Frontend Parameters**:

- Update the frontend server (`NEXT_SERVER_*`) parameters using the Lambda URL from Terraform outputs.

1. **Restart Frontend ECS Tasks**:

- Force a new deployment to pick up the updated configuration:

    > [!NOTE]
    > Replace `us-east-2` with configured region.

    ```bash
    aws ecs update-service \
        --cluster nest-staging-frontend-cluster \
        --service nest-staging-frontend-service \
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
