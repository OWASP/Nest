"""Tests for ``scripts.sync_params_runner``."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from unittest.mock import MagicMock, call

import pytest

from scripts.commands import CommandRunner
from scripts.errors import RunnerError
from scripts.sync_params_runner import (
    PARAMETER_PATH,
    PARAMETERS_PAGE_QUERY,
    RDS_PORT_QUERY,
    REDIS_PORT_QUERY,
    InfrastructureParameterSyncRunner,
)


def build_listing_response(
    parameters: list[dict[str, str]],
    page_marker: str | None = None,
) -> MagicMock:
    payload = {"parameters": parameters}
    if page_marker is not None:
        payload["nextToken"] = page_marker
    return MagicMock(returncode=0, stdout=json.dumps(payload))


def build_port_response(port: int) -> MagicMock:
    return MagicMock(returncode=0, stdout=json.dumps(port))


def build_put_call(name: str, parameter_type: str, value: str) -> call:
    return call(
        "awslocal",
        "ssm",
        "put-parameter",
        "--cli-input-json",
        json.dumps(
            {
                "Name": name,
                "Overwrite": True,
                "Type": parameter_type,
                "Value": value,
            }
        ),
        capture_output=True,
    )


def build_runner(env_file: Path) -> InfrastructureParameterSyncRunner:
    return InfrastructureParameterSyncRunner(
        commands=MagicMock(spec=CommandRunner),
        env_file=env_file,
    )


class TestInfrastructureParameterSyncRunner:
    """Tests for ``InfrastructureParameterSyncRunner`` behavior."""

    def test_read_env_values_parses_comments_blanks_and_quotes(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text(
            "# comment\n"
            "\n"
            "NOT_AN_ASSIGNMENT\n"
            "DJANGO_SECRET_KEY='quoted-secret'\n"
            'DJANGO_SLACK_BOT_TOKEN="xoxb-token"\n'
            "DJANGO_SLACK_SIGNING_SECRET=\n"
        )
        runner = build_runner(env_file)

        assert runner.read_env_values() == {
            "DJANGO_SECRET_KEY": "quoted-secret",
            "DJANGO_SLACK_BOT_TOKEN": "xoxb-token",
        }

    def test_read_env_values_raises_when_file_missing(self, tmp_path: Path) -> None:
        runner = build_runner(tmp_path / "missing.env")

        with pytest.raises(RunnerError, match="environment file not found"):
            runner.read_env_values()

    def test_sync_puts_matching_values_with_listed_types(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text(
            "DJANGO_DB_NAME=nest-db-name\n"
            "DJANGO_SECRET_KEY=django-secret\n"
            "DJANGO_SENTRY_DSN=https://key@sentry.example.io/1\n"
            "DJANGO_SLACK_SEARCH_TOKEN=\n"
        )
        commands = MagicMock(spec=CommandRunner)
        listing = [
            {"name": f"{PARAMETER_PATH}/DJANGO_DB_NAME", "type": "String"},
            {"name": f"{PARAMETER_PATH}/DJANGO_SECRET_KEY", "type": "String"},
            {
                "name": f"{PARAMETER_PATH}/DJANGO_SENTRY_DSN",
                "type": "SecureString",
            },
            {
                "name": f"{PARAMETER_PATH}/DJANGO_SLACK_SEARCH_TOKEN",
                "type": "SecureString",
            },
        ]
        commands.run.side_effect = [
            build_listing_response(listing),
            MagicMock(returncode=0),
            MagicMock(returncode=0),
        ]
        runner = InfrastructureParameterSyncRunner(
            commands=commands,
            env_file=env_file,
        )

        with caplog.at_level(logging.INFO):
            runner.sync()

        assert commands.run.call_args_list[1] == build_put_call(
            f"{PARAMETER_PATH}/DJANGO_SECRET_KEY",
            "String",
            "django-secret",
        )
        assert commands.run.call_args_list[2] == build_put_call(
            f"{PARAMETER_PATH}/DJANGO_SENTRY_DSN",
            "SecureString",
            "https://key@sentry.example.io/1",
        )
        assert "Synced 2 parameters" in caplog.text
        assert "Skipped, not allow-listed: DJANGO_DB_NAME." in caplog.text
        assert "No .env value for: DJANGO_SLACK_SEARCH_TOKEN." in caplog.text

    def test_sync_skips_parameters_not_in_allow_list(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("DJANGO_DB_NAME=nest_db_dev\n")
        commands = MagicMock(spec=CommandRunner)
        listing = [
            {"name": f"{PARAMETER_PATH}/DJANGO_DB_NAME", "type": "String"},
        ]
        commands.run.side_effect = [build_listing_response(listing)]
        runner = InfrastructureParameterSyncRunner(
            commands=commands,
            env_file=env_file,
        )

        with caplog.at_level(logging.INFO):
            runner.sync()

        assert commands.run.call_count == 1
        assert "Skipped, not allow-listed: DJANGO_DB_NAME." in caplog.text

    def test_sync_skips_selector_parameters_without_override(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("DJANGO_CONFIGURATION=Local\nDJANGO_SECRET_KEY=key\n")
        commands = MagicMock(spec=CommandRunner)
        listing = [
            {"name": f"{PARAMETER_PATH}/DJANGO_CONFIGURATION", "type": "String"},
            {"name": f"{PARAMETER_PATH}/DJANGO_SECRET_KEY", "type": "String"},
        ]
        commands.run.side_effect = [
            build_listing_response(listing),
            MagicMock(returncode=0),
        ]
        runner = InfrastructureParameterSyncRunner(
            commands=commands,
            env_file=env_file,
        )

        with caplog.at_level(logging.INFO):
            runner.sync()

        assert commands.run.call_count == 2
        assert "Skipping DJANGO_CONFIGURATION; pass an override" in caplog.text

    def test_sync_sets_configuration_override(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("DJANGO_SECRET_KEY=key\n")
        commands = MagicMock(spec=CommandRunner)
        listing = [
            {"name": f"{PARAMETER_PATH}/DJANGO_CONFIGURATION", "type": "String"},
            {"name": f"{PARAMETER_PATH}/DJANGO_SECRET_KEY", "type": "String"},
        ]
        commands.run.side_effect = [
            build_listing_response(listing),
            MagicMock(returncode=0),
            MagicMock(returncode=0),
        ]
        runner = InfrastructureParameterSyncRunner(
            commands=commands,
            env_file=env_file,
        )

        runner.sync(configuration="Local")

        assert commands.run.call_args_list[1] == build_put_call(
            f"{PARAMETER_PATH}/DJANGO_CONFIGURATION",
            "String",
            "Local",
        )

    def test_sync_sets_settings_module_override(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("DJANGO_SECRET_KEY=key\n")
        commands = MagicMock(spec=CommandRunner)
        listing = [
            {"name": f"{PARAMETER_PATH}/DJANGO_SECRET_KEY", "type": "String"},
            {"name": f"{PARAMETER_PATH}/DJANGO_SETTINGS_MODULE", "type": "String"},
        ]
        commands.run.side_effect = [
            build_listing_response(listing),
            MagicMock(returncode=0),
            MagicMock(returncode=0),
        ]
        runner = InfrastructureParameterSyncRunner(
            commands=commands,
            env_file=env_file,
        )

        runner.sync(settings_module="settings.local")

        assert commands.run.call_args_list[2] == build_put_call(
            f"{PARAMETER_PATH}/DJANGO_SETTINGS_MODULE",
            "String",
            "settings.local",
        )

    def test_sync_raises_when_override_parameter_missing(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("DJANGO_SECRET_KEY=key\n")
        commands = MagicMock(spec=CommandRunner)
        listing = [{"name": f"{PARAMETER_PATH}/DJANGO_SECRET_KEY", "type": "String"}]
        commands.run.side_effect = [build_listing_response(listing)]
        runner = InfrastructureParameterSyncRunner(
            commands=commands,
            env_file=env_file,
        )

        with pytest.raises(RunnerError, match="no SSM parameter for override"):
            runner.sync(configuration="Local")

        assert commands.run.call_count == 1

    def test_sync_paginates_parameters(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("DJANGO_ALGOLIA_APPLICATION_ID=app-id\nDJANGO_SECRET_KEY=key\n")
        commands = MagicMock(spec=CommandRunner)
        first_page = [
            {
                "name": f"{PARAMETER_PATH}/DJANGO_ALGOLIA_APPLICATION_ID",
                "type": "String",
            }
        ]
        second_page = [{"name": f"{PARAMETER_PATH}/DJANGO_SECRET_KEY", "type": "String"}]
        commands.run.side_effect = [
            build_listing_response(first_page, page_marker="token-1"),
            build_listing_response(second_page),
            MagicMock(returncode=0),
            MagicMock(returncode=0),
        ]
        runner = InfrastructureParameterSyncRunner(
            commands=commands,
            env_file=env_file,
        )

        runner.sync()

        assert commands.run.call_args_list[0] == call(
            "awslocal",
            "ssm",
            "get-parameters-by-path",
            "--max-results",
            "10",
            "--output",
            "json",
            "--path",
            PARAMETER_PATH,
            "--query",
            PARAMETERS_PAGE_QUERY,
            capture_output=True,
        )
        assert commands.run.call_args_list[1] == call(
            "awslocal",
            "ssm",
            "get-parameters-by-path",
            "--max-results",
            "10",
            "--output",
            "json",
            "--path",
            PARAMETER_PATH,
            "--query",
            PARAMETERS_PAGE_QUERY,
            "--next-token",
            "token-1",
            capture_output=True,
        )
        assert commands.run.call_count == 4

    def test_sync_raises_when_listing_fails(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("DJANGO_SECRET_KEY=key\n")
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=1, stderr="boom")
        runner = InfrastructureParameterSyncRunner(
            commands=commands,
            env_file=env_file,
        )

        with pytest.raises(RunnerError, match="get-parameters-by-path failed"):
            runner.sync()

    def test_sync_raises_when_put_fails(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("DJANGO_SECRET_KEY=key\n")
        commands = MagicMock(spec=CommandRunner)
        listing = [{"name": f"{PARAMETER_PATH}/DJANGO_SECRET_KEY", "type": "String"}]
        commands.run.side_effect = [
            build_listing_response(listing),
            MagicMock(returncode=1, stderr="boom"),
        ]
        runner = InfrastructureParameterSyncRunner(
            commands=commands,
            env_file=env_file,
        )

        with pytest.raises(RunnerError, match="put-parameter failed for"):
            runner.sync()

    def test_sync_skips_empty_env_values(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("DJANGO_SLACK_SIGNING_SECRET=\nDJANGO_SECRET_KEY=key\n")
        commands = MagicMock(spec=CommandRunner)
        listing = [
            {
                "name": f"{PARAMETER_PATH}/DJANGO_SLACK_SIGNING_SECRET",
                "type": "SecureString",
            },
            {"name": f"{PARAMETER_PATH}/DJANGO_SECRET_KEY", "type": "String"},
        ]
        commands.run.side_effect = [
            build_listing_response(listing),
            MagicMock(returncode=0),
        ]
        runner = InfrastructureParameterSyncRunner(
            commands=commands,
            env_file=env_file,
        )

        with caplog.at_level(logging.INFO):
            runner.sync()

        assert commands.run.call_count == 2
        assert "No .env value for: DJANGO_SLACK_SIGNING_SECRET." in caplog.text

    def test_sync_puts_fetched_deployment_endpoints(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("DJANGO_DB_HOST=db\nDJANGO_REDIS_HOST=cache\nDJANGO_SECRET_KEY=key\n")
        commands = MagicMock(spec=CommandRunner)
        listing = [
            {"name": f"{PARAMETER_PATH}/DJANGO_DB_HOST", "type": "String"},
            {"name": f"{PARAMETER_PATH}/DJANGO_DB_PORT", "type": "String"},
            {"name": f"{PARAMETER_PATH}/DJANGO_REDIS_AUTH_ENABLED", "type": "String"},
            {"name": f"{PARAMETER_PATH}/DJANGO_REDIS_HOST", "type": "String"},
            {"name": f"{PARAMETER_PATH}/DJANGO_REDIS_PORT", "type": "String"},
            {"name": f"{PARAMETER_PATH}/DJANGO_REDIS_USE_TLS", "type": "String"},
            {"name": f"{PARAMETER_PATH}/DJANGO_SECRET_KEY", "type": "String"},
        ]
        commands.run.side_effect = [
            build_listing_response(listing),
            build_port_response(4511),
            build_port_response(4513),
            MagicMock(returncode=0),
            MagicMock(returncode=0),
            MagicMock(returncode=0),
            MagicMock(returncode=0),
            MagicMock(returncode=0),
            MagicMock(returncode=0),
            MagicMock(returncode=0),
        ]
        runner = InfrastructureParameterSyncRunner(
            commands=commands,
            env_file=env_file,
        )

        with caplog.at_level(logging.INFO):
            runner.sync()

        assert commands.run.call_args_list[1] == call(
            "awslocal",
            "rds",
            "describe-db-instances",
            "--output",
            "json",
            "--query",
            RDS_PORT_QUERY,
            capture_output=True,
        )
        assert commands.run.call_args_list[2] == call(
            "awslocal",
            "elasticache",
            "describe-cache-clusters",
            "--output",
            "json",
            "--query",
            REDIS_PORT_QUERY,
            "--show-cache-node-info",
            capture_output=True,
        )
        assert commands.run.call_args_list[3] == build_put_call(
            f"{PARAMETER_PATH}/DJANGO_DB_HOST",
            "String",
            "localstack",
        )
        assert commands.run.call_args_list[4] == build_put_call(
            f"{PARAMETER_PATH}/DJANGO_DB_PORT",
            "String",
            "4511",
        )
        assert commands.run.call_args_list[5] == build_put_call(
            f"{PARAMETER_PATH}/DJANGO_REDIS_AUTH_ENABLED",
            "String",
            "False",
        )
        assert commands.run.call_args_list[6] == build_put_call(
            f"{PARAMETER_PATH}/DJANGO_REDIS_HOST",
            "String",
            "localstack",
        )
        assert commands.run.call_args_list[7] == build_put_call(
            f"{PARAMETER_PATH}/DJANGO_REDIS_PORT",
            "String",
            "4513",
        )
        assert commands.run.call_args_list[8] == build_put_call(
            f"{PARAMETER_PATH}/DJANGO_REDIS_USE_TLS",
            "String",
            "False",
        )
        assert (
            "Synced deployment endpoints: database localstack:4511, Redis localstack:4513."
            in caplog.text
        )

    def test_sync_raises_when_rds_fetch_fails(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("DJANGO_SECRET_KEY=key\n")
        commands = MagicMock(spec=CommandRunner)
        listing = [{"name": f"{PARAMETER_PATH}/DJANGO_DB_PORT", "type": "String"}]
        commands.run.side_effect = [
            build_listing_response(listing),
            MagicMock(returncode=1, stderr="boom"),
        ]
        runner = InfrastructureParameterSyncRunner(
            commands=commands,
            env_file=env_file,
        )

        with pytest.raises(RunnerError, match="describe-db-instances failed"):
            runner.sync()

    def test_sync_raises_when_redis_fetch_fails(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("DJANGO_SECRET_KEY=key\n")
        commands = MagicMock(spec=CommandRunner)
        listing = [{"name": f"{PARAMETER_PATH}/DJANGO_REDIS_PORT", "type": "String"}]
        commands.run.side_effect = [
            build_listing_response(listing),
            build_port_response(4511),
            MagicMock(returncode=1, stderr="boom"),
        ]
        runner = InfrastructureParameterSyncRunner(
            commands=commands,
            env_file=env_file,
        )

        with pytest.raises(RunnerError, match="describe-cache-clusters failed"):
            runner.sync()

    def test_sync_reports_missing_deployment_parameters(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("DJANGO_SECRET_KEY=key\n")
        commands = MagicMock(spec=CommandRunner)
        listing = [
            {"name": f"{PARAMETER_PATH}/DJANGO_DB_HOST", "type": "String"},
            {"name": f"{PARAMETER_PATH}/DJANGO_DB_PORT", "type": "String"},
            {"name": f"{PARAMETER_PATH}/DJANGO_SECRET_KEY", "type": "String"},
        ]
        commands.run.side_effect = [
            build_listing_response(listing),
            build_port_response(4511),
            build_port_response(4513),
            MagicMock(returncode=0),
            MagicMock(returncode=0),
            MagicMock(returncode=0),
        ]
        runner = InfrastructureParameterSyncRunner(
            commands=commands,
            env_file=env_file,
        )

        with caplog.at_level(logging.INFO):
            runner.sync()

        assert (
            "No SSM parameter for deployment endpoint(s): DJANGO_REDIS_AUTH_ENABLED, "
            "DJANGO_REDIS_HOST, DJANGO_REDIS_PORT, DJANGO_REDIS_USE_TLS." in caplog.text
        )

    def test_sync_reports_env_values_without_parameters(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text(
            "DJANGO_ELEVENLABS_API_KEY=eleven-key\nDJANGO_SLACK_CLIENT_SECRET=client-secret\n"
        )
        commands = MagicMock(spec=CommandRunner)
        listing = [
            {"name": f"{PARAMETER_PATH}/DJANGO_SECRET_KEY", "type": "String"},
        ]
        commands.run.side_effect = [build_listing_response(listing)]
        runner = InfrastructureParameterSyncRunner(
            commands=commands,
            env_file=env_file,
        )

        with caplog.at_level(logging.INFO):
            runner.sync()

        assert "No SSM parameter for: DJANGO_SLACK_CLIENT_SECRET." in caplog.text
        assert "DJANGO_ELEVENLABS_API_KEY" not in caplog.text

    def test_sync_deployment_endpoints_puts_localstack_values(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("DJANGO_SECRET_KEY=django-secret\n")
        commands = MagicMock(spec=CommandRunner)
        listing = [
            {"name": f"{PARAMETER_PATH}/DJANGO_DB_HOST", "type": "String"},
            {"name": f"{PARAMETER_PATH}/DJANGO_DB_PORT", "type": "String"},
            {"name": f"{PARAMETER_PATH}/DJANGO_REDIS_AUTH_ENABLED", "type": "String"},
            {"name": f"{PARAMETER_PATH}/DJANGO_REDIS_HOST", "type": "String"},
            {"name": f"{PARAMETER_PATH}/DJANGO_REDIS_PORT", "type": "String"},
            {"name": f"{PARAMETER_PATH}/DJANGO_REDIS_USE_TLS", "type": "String"},
            {"name": f"{PARAMETER_PATH}/DJANGO_SECRET_KEY", "type": "String"},
        ]
        commands.run.side_effect = [
            build_listing_response(listing),
            build_port_response(4511),
            build_port_response(4513),
            MagicMock(returncode=0),
            MagicMock(returncode=0),
            MagicMock(returncode=0),
            MagicMock(returncode=0),
            MagicMock(returncode=0),
            MagicMock(returncode=0),
        ]
        runner = InfrastructureParameterSyncRunner(
            commands=commands,
            env_file=env_file,
        )

        with caplog.at_level(logging.INFO):
            runner.sync_deployment_endpoints()

        assert commands.run.call_count == 9
        assert commands.run.call_args_list[3] == build_put_call(
            f"{PARAMETER_PATH}/DJANGO_DB_HOST",
            "String",
            "localstack",
        )
        assert commands.run.call_args_list[4] == build_put_call(
            f"{PARAMETER_PATH}/DJANGO_DB_PORT",
            "String",
            "4511",
        )
        assert commands.run.call_args_list[5] == build_put_call(
            f"{PARAMETER_PATH}/DJANGO_REDIS_AUTH_ENABLED",
            "String",
            "False",
        )
        assert commands.run.call_args_list[6] == build_put_call(
            f"{PARAMETER_PATH}/DJANGO_REDIS_HOST",
            "String",
            "localstack",
        )
        assert commands.run.call_args_list[7] == build_put_call(
            f"{PARAMETER_PATH}/DJANGO_REDIS_PORT",
            "String",
            "4513",
        )
        assert commands.run.call_args_list[8] == build_put_call(
            f"{PARAMETER_PATH}/DJANGO_REDIS_USE_TLS",
            "String",
            "False",
        )
        assert (
            "Synced deployment endpoints: database localstack:4511, Redis localstack:4513."
            in caplog.text
        )

    def test_sync_deployment_endpoints_skips_when_no_parameters(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("DJANGO_SECRET_KEY=django-secret\n")
        commands = MagicMock(spec=CommandRunner)
        listing = [{"name": f"{PARAMETER_PATH}/DJANGO_SECRET_KEY", "type": "String"}]
        commands.run.side_effect = [build_listing_response(listing)]
        runner = InfrastructureParameterSyncRunner(
            commands=commands,
            env_file=env_file,
        )

        with caplog.at_level(logging.INFO):
            runner.sync_deployment_endpoints()

        assert commands.run.call_count == 1
        assert "No deployment endpoint parameters found to sync." in caplog.text
        assert "No SSM parameter for deployment endpoint(s): DJANGO_DB_HOST" in caplog.text

    def test_sync_deployment_endpoints_raises_when_rds_fetch_fails(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("DJANGO_SECRET_KEY=django-secret\n")
        commands = MagicMock(spec=CommandRunner)
        listing = [{"name": f"{PARAMETER_PATH}/DJANGO_DB_PORT", "type": "String"}]
        commands.run.side_effect = [
            build_listing_response(listing),
            MagicMock(returncode=1, stderr="boom"),
        ]
        runner = InfrastructureParameterSyncRunner(
            commands=commands,
            env_file=env_file,
        )

        with pytest.raises(RunnerError, match="describe-db-instances failed"):
            runner.sync_deployment_endpoints()
