# Infrastructure

This document provides instructions on how to setup the infrastructure for this project.

## Prerequisites

Ensure you have the following setup/installed:

- Setup Project: [CONTRIBUTING.md](https://github.com/OWASP/Nest/blob/main/CONTRIBUTING.md)
- Terraform: [Terraform Documentation](https://developer.hashicorp.com/terraform/docs)
- AWS CLI: [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- An AWS account.
Note: Refer to the respective `README.md` files for more information.

## External Documentation

- [OWASP Nest DeepWiki](https://deepwiki.com/OWASP/Nest/4.3-aws-infrastructure)

## Terraform Docs

Refresh generated Terraform reference sections locally with:

```bash
make terraform-docs-infrastructure
```

## Setting up the infrastructure

Follow these steps to set up the infrastructure:

> [!NOTE]
> All change directory (`cd`) commands are relative to the project root.

1. **Setup State (one-time setup)**:

- Prerequisite: Create a `nest-state` IAM user with the policies defined in `infrastructure/state/README.md`.

- Navigate to the state directory:

    ```bash
    cd infrastructure/state/
    ```

  > [!NOTE]
  > Optionally change the region: set `aws_region` in a `.tfvars` file.

- Initialize Terraform if needed:

    ```bash
    terraform init
    ```

- Apply the changes to create the state resources:

    ```bash
    terraform apply
    ```

  > [!NOTE]
  > Copy the state bucket names from the output.
  > It is recommended to not destroy the state resources unless absolutely necessary.

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

  > [!NOTE]
  > Update `AWS_ROLE_EXTERNAL_ID` in `terraform.tfvars` with a randomly generated ID of your choice.
  > This ID is required in the next step.

- Copy the contents from the template file into your new terraform backend file:

    ```bash
    cp terraform.tfbackend.example terraform.tfbackend
    ```

  > [!NOTE]
  > Update the state bucket name in `terraform.tfbackend` with the name of the state bucket (`state_bucket_names["bootstrap"]`) created in the state creation step.

- Initialize Terraform if needed:

    ```bash
    terraform init -backend-config=terraform.tfbackend
    ```

- Apply the changes to create the bootstrap resources:

    ```bash
    terraform apply
    ```

1. **Setup Main Infrastructure (staging)**:

> [!NOTE]
> This document has steps to deploy the `staging` environment.

Prerequisite: Create a `nest-staging` IAM user with the policies defined in `infrastructure/live/README.md`.
This user must assume the role `nest-staging-terraform` created in the bootstrap step.
To do this locally:

- Create a new profile at `~/.aws/credentials`:

    ```bash
    [nest-staging-identity]
    aws_access_key_id = AWS_ACCESS_KEY_ID
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY
    ```

- Create a new profile at `~/.aws/config`:

    > [!NOTE]
    > Use the previously generated `AWS_ROLE_EXTERNAL_ID`.

    ```bash
    [profile nest-staging]
    external_id = AWS_ROLE_EXTERNAL_ID
    role_arn = arn:aws:iam::AWS_ACCOUNT_ID:role/nest-staging-terraform
    source_profile = nest-staging-identity
    ```

    Use this profile for all `staging` related terraform commands.

- Navigate to the main infrastructure directory:

    ```bash
    cd infrastructure/live/
    ```

- Copy the contents from the template file into your new local terraform variables file:

    ```bash
    cp terraform.tfvars.staging.example terraform.tfvars
    ```

- Copy the contents from the template file into your new local terraform backend file:

    ```bash
    cp terraform.tfbackend.staging.example terraform.tfbackend
    ```

  > [!NOTE]
  > Update the state bucket name in `terraform.tfbackend` with the name of the state bucket created in the previous step.
  > Update `backend_image_tag` and `frontend_image_tag` variables with a unique tag (for example, a commit SHA or timestamp); do not reuse `latest` when tags are immutable.
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

## Populate ECR Repositories

ECR Repositories are used to store images used by ECS (Frontend + Backend + Scheduled Tasks)

> [!NOTE]
> Ensure you are in the project root.

1. **Login to ECR**:

- Login to the Elastic Container Registry using the following command:

    > [!WARNING]
    > Configure a credential helper instead of using following command to login.

    ```bash
    aws ecr get-login-password --region AWS_REGION | docker login --username AWS --password-stdin AWS_ACCOUNT_ID.dkr.ecr.AWS_REGION.amazonaws.com
    ```

1. **Upload backend image to ECR**:

> [!NOTE]
> The `latest` tag is used in these example commands. ECR repository tags are `IMMUTABLE`.
> Pushing images with an existing tag will fail.

- Build the backend image using the following command:

    ```bash
    docker build -t nest-staging-backend:latest -f docker/backend/Dockerfile backend/
    ```

- Tag the image:

    ```bash
    docker tag nest-staging-backend:latest AWS_ACCOUNT_ID.dkr.ecr.AWS_REGION.amazonaws.com/nest-staging-backend:latest
    ```

- Push the image:

    ```bash
    docker push AWS_ACCOUNT_ID.dkr.ecr.AWS_REGION.amazonaws.com/nest-staging-backend:latest
    ```

1. **Upload frontend image to ECR**:

> [!NOTE]
> The `latest` tag is used in these example commands. ECR repository tags are `IMMUTABLE`.
> Pushing images with an existing tag will fail.

- Build the frontend image using the following command:

    > [!NOTE]
    > Make sure to update the frontend `.env` file with correct `NEXT_PUBLIC_*` variables.
    > These are injected at build time.

    ```bash
    docker build -t nest-staging-frontend:latest -f docker/frontend/Dockerfile frontend/
    ```

- Tag the image:

    ```bash
    docker tag nest-staging-frontend:latest AWS_ACCOUNT_ID.dkr.ecr.AWS_REGION.amazonaws.com/nest-staging-frontend:latest
    ```

- Push the image:

    ```bash
    docker push AWS_ACCOUNT_ID.dkr.ecr.AWS_REGION.amazonaws.com/nest-staging-frontend:latest
    ```

## Setup Database

Migrate and load data into the new database.

1. **Shared bucket and `nest.dump`**

- Terraform (`module.storage` → `shared_data_bucket` in `infrastructure/modules/storage`) provisions **`owasp-nest-shared-data`**. Public read of **`nest.dump`** at the bucket root (HTTPS) is for **local/CI** only. ECS **load-data** uses the **fixtures** bucket at **`databases/nest.dump`** per environment.
- **Dump:** `make dump-data` → `backend/data/nest.dump`. **Upload / fetch:** `make upload-nest-dump` / `make fetch-nest-dump` (host AWS credentials; optional **`SHARED_DATA_BUCKET`**).
- **CLI** (after `cd infrastructure/live`):

    ```bash
    aws s3 cp ../../backend/data/nest.dump "s3://$(terraform output -raw shared_data_bucket_name)/nest.dump"
    ```

1. **Run ECS Tasks**:

Run the following commands to execute ECS tasks with the correct network configuration:

> [!NOTE]
> Ensure you are in the `infrastructure/live` directory.

1. Set variables from Terraform outputs

> [!NOTE]
> Ensure you have `jq` installed.

```bash
CLUSTER=$(terraform output -raw tasks_cluster_name)
SECURITY_GROUP=$(terraform output -raw tasks_security_group_id)
SUBNETS=$(terraform output -json tasks_subnet_ids | jq -r 'join(",")')
NAT_ENABLED=$(terraform output -raw nat_gateway_enabled)
ASSIGN_PUBLIC_IP=$([ "$NAT_ENABLED" = "true" ] && echo "DISABLED" || echo "ENABLED")
```

> [!NOTE]
> Replace `AWS_REGION` in each command with appropriate region.
> Please wait for a task to be complete before running the next task.
> To view the status of a task, use the AWS Console.

1. Run migrate task and wait for it to be complete:

```bash
aws ecs run-task \
  --cluster "$CLUSTER" \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SECURITY_GROUP],assignPublicIp=$ASSIGN_PUBLIC_IP}" \
  --task-definition nest-staging-migrate \
  --region AWS_REGION
```

1. Run load-data task and wait for it to be complete:

```bash
aws ecs run-task \
  --cluster "$CLUSTER" \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SECURITY_GROUP],assignPublicIp=$ASSIGN_PUBLIC_IP}" \
  --task-definition nest-staging-load-data \
  --region AWS_REGION
```

1. Run index-data task and wait for it to be complete:

```bash
aws ecs run-task \
  --cluster "$CLUSTER" \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SECURITY_GROUP],assignPublicIp=$ASSIGN_PUBLIC_IP}" \
  --task-definition nest-staging-index-data \
  --region AWS_REGION
```

<details>
<summary>Manual AWS Console Instructions (Alternative)</summary>

- Head over to Elastic Container Service in the AWS Console.
- Click on `nest-staging-migrate` in `Task Definitions` section.
- Select the task definition revision.
- Click Deploy > Run Task.
- Use the following configuration:
  - Environment: Cluster: `nest-staging-tasks-cluster`
  - Networking:
    - VPC: `nest-staging-vpc`
    - Subnets: Choose a private subnet if NAT Gateway is enabled, public otherwise (default).
    - Security group name: select the ECS security group (e.g. `nest-staging-tasks-sg`).
    - Public IP: Turned off if NAT Gateway is enabled, Turned on otherwise (default).
- Click "Create"
- The task is now running... Click on the task ID to view Logs, Status, etc.
- Follow the same steps for `nest-staging-load-data` and `nest-staging-index-data`.

</details>

## Configure Domain

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

## Redeploy Frontend and Backend

1. **Configure Frontend Parameters**:

- Update the frontend server (`NEXT_SERVER_*`) parameters using the backend ALB URL from Terraform outputs.
- Populate all `DJANGO_*` parameters that have `to-be-set-in-aws-console` value.

1. **Restart Backend ECS Tasks**:

- Force a new deployment to pick up the updated configuration:

    ```bash
    aws ecs update-service \
        --cluster nest-staging-backend-cluster \
        --service nest-staging-backend-service \
        --force-new-deployment \
        --region AWS_REGION
    ```

1. **Restart Frontend ECS Tasks**:

- Force a new deployment to pick up the updated configuration:

    ```bash
    aws ecs update-service \
        --cluster nest-staging-frontend-cluster \
        --service nest-staging-frontend-service \
        --force-new-deployment \
        --region AWS_REGION
    ```

## Cleaning Up

- Ensure all buckets and ECR repositories are empty.

> [!NOTE]
> Some resources have `prevent_destroy` set to `true`. Please set it to `false` before destruction.

- To destroy Terraform infrastructure:

  ```bash
  terraform destroy
  ```
