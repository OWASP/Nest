"""Tests for ``scripts.aws``."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

from scripts.aws import aws_client


class TestAwsClient:
    """Tests for the ``aws_client`` factory."""

    @patch.dict(os.environ, {}, clear=True)
    @patch("scripts.aws.boto3.client")
    def test_aws_client_points_at_localstack(self, mock_boto3_client: MagicMock) -> None:
        localstack = MagicMock()
        localstack.api_url = "http://custom-host:9999"  # NOSONAR: Test-only LocalStack HTTP.

        result = aws_client("s3", localstack=localstack)

        assert result is mock_boto3_client.return_value
        mock_boto3_client.assert_called_once_with(
            "s3",
            endpoint_url="http://custom-host:9999",
            region_name="us-east-2",
            aws_access_key_id="test",
            aws_secret_access_key="test",  # noqa: S106
        )

    @patch.dict(os.environ, {"AWS_DEFAULT_REGION": "eu-west-1"}, clear=True)
    @patch("scripts.aws.boto3.client")
    def test_aws_client_uses_region_from_environment(self, mock_boto3_client: MagicMock) -> None:
        localstack = MagicMock()
        localstack.api_url = "http://custom-host:9999"  # NOSONAR: Test-only LocalStack HTTP.

        aws_client("ssm", localstack=localstack)

        assert mock_boto3_client.call_args.kwargs["region_name"] == "eu-west-1"

    @patch.dict(os.environ, {}, clear=True)
    @patch("scripts.aws.boto3.client")
    @patch("scripts.aws.LocalStack")
    def test_aws_client_defaults_to_localstack_instance(
        self, mock_localstack_cls: MagicMock, mock_boto3_client: MagicMock
    ) -> None:
        default = MagicMock()
        default.api_url = "http://localhost:4566"  # NOSONAR: Test-only LocalStack HTTP.
        mock_localstack_cls.return_value = default

        aws_client("ecr")

        mock_localstack_cls.assert_called_once_with()
        assert mock_boto3_client.call_args.kwargs["endpoint_url"] == "http://localhost:4566"
