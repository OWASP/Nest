# OWASP Nest - AWS Infrastructure Operational Guide

This document contains the complete operational guide for deploying and managing the OWASP Nest application infrastructure on AWS using Terraform. The project is designed to be modular, reusable, and secure, following industry best practices for managing infrastructure in a collaborative, open-source environment.

## Project Overview

This Terraform setup provisions a multi-environment (dev, staging, prod) infrastructure for the OWASP Nest application. It leverages a modular design to manage networking, compute, data, and storage resources independently.

-   **Environments:** Code is organized under `environments/` to provide strong isolation between `dev`, `staging`, and `production`.
-   **Modules:** Reusable components are defined in `modules/` for consistency and maintainability.
-   **State Management:** Terraform state is stored remotely in an S3 bucket. State locking is managed by DynamoDB to prevent conflicts and ensure safe, concurrent operations by multiple contributors.
-   **Security:** All sensitive data is managed via AWS Secrets Manager. Network access is restricted using a least-privilege security group model.

## Phased Rollout Plan

The infrastructure will be built and deployed in a series of focused Pull Requests to ensure each foundational layer is stable and well-reviewed before building on top of it.

1.  **Phase 1: Foundational Networking (`modules/network`)**
2.  **Phase 2: Data & Storage Tiers (`modules/database`, `modules/storage`, `modules/cache`)**
3.  **Phase 3: Compute & IAM (`modules/compute`, `modules/iam`)**

This document will be updated as each phase is completed.

## Prerequisites

Before you begin, ensure you have the following tools installed and configured:

1.  **Terraform:** [Install Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli) (Version 1.3.0 or newer recommended).
2.  **AWS CLI:** [Install and configure the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html). You must have an active AWS profile configured with credentials that have sufficient permissions to create the resources.
3.  **pre-commit:** [Install pre-commit](https://pre-commit.com/#installation) (`pip install pre-commit`).

## Initial Setup (One-Time)

This infrastructure requires an S3 bucket and a DynamoDB table for managing Terraform's remote state. These must be created manually before you can run `terraform init`.

**Note:** The following commands are examples. Please ensure the chosen S3 bucket name is globally unique.

1.  **Define Environment Variables (Recommended):**
    ```bash
    # Run these in your terminal to make the next steps easier
    export AWS_REGION="us-east-1" # Or your preferred AWS region
    export TF_STATE_BUCKET="owasp-nest-tfstate-$(aws sts get-caller-identity --query Account --output text)" # Creates a unique bucket name
    export TF_STATE_LOCK_TABLE="owasp-nest-tf-locks"
    ```

2.  **Create the S3 Bucket for Terraform State:**
    *This bucket will store the `.tfstate` file, which is Terraform's map of your infrastructure.*
    ```bash
    if [ "${AWS_REGION}" = "us-east-1" ]; then
      aws s3api create-bucket --bucket "${TF_STATE_BUCKET}" --region "${AWS_REGION}"
    else
      aws s3api create-bucket \
        --bucket "${TF_STATE_BUCKET}" \
        --region "${AWS_REGION}" \
        --create-bucket-configuration LocationConstraint=${AWS_REGION}
    fi

    aws s3api put-bucket-versioning \
      --bucket ${TF_STATE_BUCKET} \
      --versioning-configuration Status=Enabled


    aws s3api put-public-access-block \
      --bucket "${TF_STATE_BUCKET}" \
      --public-access-block-configuration 'BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true'

    aws s3api put-bucket-encryption \
      --bucket "${TF_STATE_BUCKET}" \
      --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
    ```

3.  **Create the DynamoDB Table for State Locking:**
    *This table prevents multiple people from running `terraform apply` at the same time, which could corrupt the state file.*
    ```bash
    aws dynamodb create-table \
      --table-name ${TF_STATE_LOCK_TABLE} \
      --attribute-definitions AttributeName=LockID,AttributeType=S \
      --key-schema AttributeName=LockID,KeyType=HASH \
      --billing-mode PAY_PER_REQUEST \
      --region ${AWS_REGION}
    ```
    *(Note: Switched to `PAY_PER_REQUEST` billing mode, which is more cost-effective for the infrequent use of a lock table).*

4.  **Install Pre-commit Hooks:**
    *From the root of the repository, run this once to set up the automated code quality checks.*
    ```bash
    pre-commit install
    ```

## Secret Population

This project provisions placeholders for secrets in AWS Secrets Manager but does **not** populate them with values. You must do this manually for each environment.

1.  Navigate to the **AWS Secrets Manager** console in the correct region.
2.  Find the secrets created by Terraform (e.g., `owasp-nest/dev/AppSecrets`, `owasp-nest/dev/DbCredentials`).
3.  Click on a secret and choose **"Retrieve secret value"**.
4.  Click **"Edit"** and populate the secret values.

    -   **For `DbCredentials`:** Use the "Plaintext" tab and create a JSON structure. Terraform will automatically generate a strong password, but you can override it here if needed.
        ```json
        {
          "username": "nestadmin",
          "password": "a-very-strong-and-long-password"
        }
        ```

    -   **For `AppSecrets`:** Use the "Plaintext" tab and create a key/value JSON structure for all required application secrets.
        ```json
        {
          "DJANGO_SECRET_KEY": "generate-a-strong-random-key-here",
          "DJANGO_ALGOLIA_WRITE_API_KEY": "your-algolia-key",
          "NEXT_PUBLIC_SENTRY_DSN": "your-sentry-dsn",
          "GITHUB_TOKEN": "your-github-token"
        }
        ```
5.  Save the secret. Repeat for all required secrets and all environments.

## Deployment Workflow

To deploy an environment, navigate to its directory and run the standard Terraform workflow.

1.  **Navigate to the Environment Directory:**
    ```bash
    cd Terraform/environments/Dev
    ```

2.  **Create a `terraform.tfvars` file:**
    *Copy the example file. This file is where you will customize variables for the environment.*
    ```bash
    cp terraform.tfvars.example terraform.tfvars
    # Now edit terraform.tfvars with your specific values (e.g., your AWS account ID, desired region).
    ```

3.  **Initialize Terraform:**
    *This downloads the necessary providers and configures the S3 backend.*
    ```bash
    terraform init
    ```

4.  **Plan the Deployment:**
    *This creates an execution plan and shows you what changes will be made. Always review this carefully.*
    ```bash
    terraform plan
    ```

5.  **Apply the Changes:**
    *This provisions the infrastructure on AWS. You will be prompted to confirm.*
    ```bash
    terraform apply
    ```

## Module Overview

-   **`modules/network`**: Creates the foundational networking layer, including the VPC, subnets, NAT Gateway, and Application Load Balancer.
-   **`modules/database`**: Provisions the AWS RDS for PostgreSQL instance, including its subnet group and security group.
-   **`modules/cache`**: Provisions the AWS ElastiCache for Redis cluster.
-   **`modules/storage`**: Creates the S3 buckets for public static assets and private media uploads, configured with secure defaults.
-   **`modules/compute`**: Provisions all compute resources: the ECS Fargate service for the frontend, the EC2 instance for cron jobs, and the necessary IAM roles and security groups for all services. It also configures the ALB routing rules.
-   **`modules/iam`**: (Future) A dedicated module for creating the various IAM roles.