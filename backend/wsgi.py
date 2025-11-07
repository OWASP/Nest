"""WSGI config for OWASP Nest project."""

import os
from pathlib import Path

import boto3


def populate_environ_from_ssm():
    """Populate environment variables from AWS Systems Manager Parameter Store."""
    if not (ssm_param_path := os.getenv("AWS_SYSTEMS_MANAGER_PARAM_STORE_PATH")):
        return

    client = boto3.client("ssm")
    paginator = client.get_paginator("get_parameters_by_path")
    response_iterator = paginator.paginate(Path=ssm_param_path, WithDecryption=True)

    for page in response_iterator:
        for param in page["Parameters"]:
            os.environ[Path(param["Name"]).name] = param["Value"]


populate_environ_from_ssm()


def _populate_environ_from_ssm():
    ssm_param_path = os.getenv("AWS_SYSTEMS_MANAGER_PARAM_STORE_PATH")
    if not ssm_param_path:
        return

    from pathlib import Path

    import boto3

    client = boto3.client("ssm")
    paginator = client.get_paginator("get_parameters_by_path")
    response_iterator = paginator.paginate(Path=ssm_param_path, WithDecryption=True)

    for page in response_iterator:
        for param in page["Parameters"]:
            os.environ[Path(param["Name"]).name] = param["Value"]


_populate_environ_from_ssm()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.local")
os.environ.setdefault("DJANGO_CONFIGURATION", "Local")

from configurations.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
