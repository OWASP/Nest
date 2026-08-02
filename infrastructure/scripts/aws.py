"""AWS client factory pointed at LocalStack."""

from __future__ import annotations

import os
from typing import Any

import boto3

from scripts.localstack import LocalStack

AWS_REGION = "us-east-2"
AWS_ACCESS_KEY_ID = "test"
AWS_SECRET_ACCESS_KEY = "test"  # noqa: S105


def aws_client(
    service: str,
    *,
    region: str | None = None,
    localstack: LocalStack | None = None,
) -> Any:
    """Return a boto3 client for ``service`` pointed at LocalStack.

    Args:
        service (str): The AWS service name, e.g. ``s3``, ``ssm`` or ``ecr``.
        region (str, optional): The AWS region. Defaults to the AWS_DEFAULT_REGION
            environment variable or ``us-east-2``.
        localstack (LocalStack, optional): The LocalStack manager used to derive the
            endpoint URL. Defaults to a default ``LocalStack`` instance.

    Returns:
        Any: A configured boto3 client.

    """
    return boto3.client(
        service,
        endpoint_url=(localstack or LocalStack()).api_url,
        region_name=region or os.environ.get("AWS_DEFAULT_REGION", AWS_REGION),
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", AWS_ACCESS_KEY_ID),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", AWS_SECRET_ACCESS_KEY),
    )
