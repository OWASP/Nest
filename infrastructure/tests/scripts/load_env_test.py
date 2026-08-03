"""Tests for ``scripts.load_env``."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from scripts.errors import MissingEnvFileError
from scripts.load_env import TERRAFORM_PARAMETER_TYPES, LoadEnv, parameter_type


def write_env_file(path: Path, content: str) -> None:
    """Create a .env file at ``path``, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture
def ssm_client() -> MagicMock:
    """Return a mock SSM client."""
    return MagicMock()


@pytest.fixture
def loader(ssm_client: MagicMock, tmp_path: Path) -> Iterator[LoadEnv]:
    """Yield a LoadEnv pointed at the given SSM client and a temp repo root."""
    with patch("scripts.load_env.aws_client", return_value=ssm_client):
        yield LoadEnv(localstack=MagicMock(), root_dir=tmp_path)


class TestParameterType:
    """Tests for the SSM parameter type classifier."""

    def test_returns_secure_string_for_secret_names(self) -> None:
        for name in (
            "DJANGO_ELEVENLABS_API_KEY",
            "DJANGO_REDIS_PASSWORD",
            "DJANGO_SECRET_KEY",
            "DJANGO_SENTRY_DSN",
            "DJANGO_SLACK_CLIENT_SECRET",
            "GITHUB_TOKEN",
        ):
            assert parameter_type(name) == "SecureString"

    def test_returns_string_for_plain_names(self) -> None:
        for name in ("DJANGO_CONFIGURATION", "NEXT_PUBLIC_API_URL"):
            assert parameter_type(name) == "String"

    def test_uses_terraform_type_when_name_lacks_secret_hint(self) -> None:
        assert parameter_type("DJANGO_ALGOLIA_APPLICATION_ID") == "SecureString"

    def test_terraform_parameter_types_are_authoritative(self) -> None:
        for name, param_type in TERRAFORM_PARAMETER_TYPES.items():
            assert parameter_type(name) == param_type


class TestGetEnvVars:
    """Tests for parsing .env files."""

    def test_returns_parsed_variables(self, loader: LoadEnv, tmp_path: Path) -> None:
        env_file = tmp_path / "backend" / ".env.localstack"
        write_env_file(env_file, "DJANGO_CONFIGURATION=Local\nGITHUB_TOKEN=secret\n")

        assert loader.get_env_vars(env_file) == {
            "DJANGO_CONFIGURATION": "Local",
            "GITHUB_TOKEN": "secret",
        }

    def test_drops_valueless_keys(self, loader: LoadEnv, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        write_env_file(env_file, "EMPTY=\nBARE\nFOO=bar\n")

        assert loader.get_env_vars(env_file) == {"EMPTY": "", "FOO": "bar"}

    def test_raises_when_file_missing(self, loader: LoadEnv, tmp_path: Path) -> None:
        missing = tmp_path / "missing.env"

        with pytest.raises(MissingEnvFileError, match=r"missing\.env"):
            loader.get_env_vars(missing)


class TestPrefix:
    """Tests for the SSM parameter prefix."""

    @patch.dict(os.environ, {}, clear=True)
    def test_defaults_to_local(self, loader: LoadEnv) -> None:
        assert loader.prefix == "/nest/local"

    @patch.dict(os.environ, {"ENVIRONMENT": "staging"}, clear=True)
    def test_uses_environment(self, loader: LoadEnv) -> None:
        assert loader.prefix == "/nest/staging"


class TestUpload:
    """Tests for uploading parameters to SSM."""

    def test_uploads_parameters_with_types(
        self, loader: LoadEnv, ssm_client: MagicMock, tmp_path: Path
    ) -> None:
        write_env_file(
            tmp_path / "backend" / ".env.localstack",
            "DJANGO_CONFIGURATION=Local\nGITHUB_TOKEN=secret\n",
        )
        write_env_file(
            tmp_path / "frontend" / ".env.localstack",
            "NEXT_PUBLIC_API_URL=/\nNEXTAUTH_SECRET=abc\n",
        )

        assert loader.upload() == 4

        expected = [
            ("/nest/local/DJANGO_CONFIGURATION", "Local", "String"),
            ("/nest/local/GITHUB_TOKEN", "secret", "SecureString"),
            ("/nest/local/NEXT_PUBLIC_API_URL", "/", "String"),
            ("/nest/local/NEXTAUTH_SECRET", "abc", "SecureString"),
        ]
        calls = ssm_client.put_parameter.call_args_list
        assert len(calls) == len(expected)
        for call, (name, value, param_type) in zip(calls, expected, strict=False):
            assert call.kwargs == {
                "Name": name,
                "Value": value,
                "Type": param_type,
                "Overwrite": False,
            }

    def test_overwrite_flag(self, loader: LoadEnv, ssm_client: MagicMock, tmp_path: Path) -> None:
        write_env_file(tmp_path / "backend" / ".env.localstack", "DJANGO_CONFIGURATION=Local\n")
        write_env_file(tmp_path / "frontend" / ".env.localstack", "")

        loader.upload(overwrite=True)

        ssm_client.put_parameter.assert_called_once_with(
            Name="/nest/local/DJANGO_CONFIGURATION",
            Value="Local",
            Type="String",
            Overwrite=True,
        )

    def test_dry_run_does_not_upload(
        self, loader: LoadEnv, ssm_client: MagicMock, tmp_path: Path
    ) -> None:
        write_env_file(tmp_path / "backend" / ".env.localstack", "DJANGO_CONFIGURATION=Local\n")
        write_env_file(tmp_path / "frontend" / ".env.localstack", "GITHUB_TOKEN=secret\n")

        assert loader.upload(dry_run=True) == 2

        ssm_client.put_parameter.assert_not_called()

    def test_skips_empty_values(
        self, loader: LoadEnv, ssm_client: MagicMock, tmp_path: Path
    ) -> None:
        write_env_file(
            tmp_path / "backend" / ".env.localstack",
            "DJANGO_CONFIGURATION=Local\nDJANGO_SLACK_BOT_TOKEN=\n",
        )
        write_env_file(tmp_path / "frontend" / ".env.localstack", "")

        assert loader.upload() == 1

        ssm_client.put_parameter.assert_called_once()

    def test_skips_existing_parameters(
        self, loader: LoadEnv, ssm_client: MagicMock, tmp_path: Path
    ) -> None:
        ssm_client.put_parameter.side_effect = ClientError(
            {"Error": {"Code": "ParameterAlreadyExists", "Message": "exists"}},
            "PutParameter",
        )
        write_env_file(tmp_path / "backend" / ".env.localstack", "DJANGO_CONFIGURATION=Local\n")
        write_env_file(tmp_path / "frontend" / ".env.localstack", "")

        assert loader.upload() == 0

        ssm_client.put_parameter.assert_called_once()

    def test_raises_other_client_errors(
        self, loader: LoadEnv, ssm_client: MagicMock, tmp_path: Path
    ) -> None:
        ssm_client.put_parameter.side_effect = ClientError(
            {"Error": {"Code": "ValidationError", "Message": "boom"}},
            "PutParameter",
        )
        write_env_file(tmp_path / "backend" / ".env.localstack", "DJANGO_CONFIGURATION=Local\n")
        write_env_file(tmp_path / "frontend" / ".env.localstack", "")

        with pytest.raises(ClientError):
            loader.upload()

    def test_raises_when_env_file_missing(self, loader: LoadEnv, tmp_path: Path) -> None:
        with pytest.raises(MissingEnvFileError):
            loader.upload()
