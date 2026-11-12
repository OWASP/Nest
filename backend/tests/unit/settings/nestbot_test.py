"""Check Slack routing with fresh Django configuration imports."""

import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    ("module", "configuration", "slack_enabled", "ai_enabled"),
    [
        ("settings.nestbot", "Staging", True, True),
        ("settings.staging", "Staging", True, True),
        ("settings.nestbot_healthcheck", "Staging", False, True),
        ("settings.production", "Production", True, False),
        ("settings.local", "Local", True, True),
    ],
)
@pytest.mark.parametrize("ai_override", [None, "True", "False"])
def test_slack_configuration(module, configuration, slack_enabled, ai_enabled, ai_override):
    # SlackConfig and urlpatterns are initialized at import time; use a fresh process.
    """Check routing and AI defaults using a fresh configuration process."""
    result = subprocess.run(  # noqa: S603 -- fixed code and repository-owned parameters
        [
            sys.executable,
            "-c",
            """
import sys
from unittest.mock import patch

with patch("slack_sdk.WebClient.auth_test", return_value={
    "ok": True, "team_id": "T123", "user_id": "U123", "bot_id": "B123",
}), patch("sentry_sdk.init"):
    from configurations import importer
    importer.install()
    import django
    django.setup()

from django.conf import settings
from django.urls import Resolver404, resolve
from apps.slack.apps import SlackConfig

enabled = sys.argv[1] == "True"
assert settings.ENVIRONMENT == sys.argv[2]
assert settings.NESTBOT_AI_ASSISTANT_ENABLED == (sys.argv[3] == "True")
assert bool(SlackConfig.app) == enabled
assert settings.SLACK_COMMANDS_ENABLED == enabled
assert settings.SLACK_EVENTS_ENABLED == enabled
for endpoint in ("commands", "events", "interactivity"):
    try:
        match = resolve(f"/integrations/slack/{endpoint}/")
    except Resolver404:
        assert not enabled
    else:
        assert enabled
        assert match.func.__name__ == "slack_request_handler"
""",
            str(slack_enabled),
            configuration,
            str(ai_enabled if ai_override is None else ai_override == "True"),
        ],
        env={
            **{
                key: value
                for key, value in os.environ.items()
                if key != "DJANGO_NESTBOT_AI_ASSISTANT_ENABLED"
            },
            **(
                {"DJANGO_NESTBOT_AI_ASSISTANT_ENABLED": ai_override}
                if ai_override is not None
                else {}
            ),
            "PYTHONPATH": str(Path(__file__).resolve().parents[3] / "src"),
            "DJANGO_CONFIGURATION": configuration,
            "DJANGO_SETTINGS_MODULE": module,
            "DJANGO_AWS_STORAGE_BUCKET_NAME": "unit-test",
            "DJANGO_GITHUB_APP_ID": "unit-test",
            "DJANGO_GITHUB_APP_INSTALLATION_ID": "unit-test",
            "DJANGO_SENTRY_DSN": "https://unit-test@localhost/1",
            "DJANGO_SLACK_BOT_TOKEN": "xoxb-unit-test",
            "DJANGO_SLACK_SIGNING_SECRET": "unit-test",
        },
        capture_output=True,
        check=False,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_worker_probe_does_not_authenticate_with_slack(monkeypatch):
    """The worker probe uses dedicated health-check settings with Slack disabled."""
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "settings.nestbot")
    monkeypatch.setenv("DJANGO_CONFIGURATION", "Staging")
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            """
from unittest.mock import patch
from configurations.management import execute_from_command_line

with patch("slack_sdk.WebClient.auth_test", side_effect=AssertionError("Slack probe")), \\
     patch("sentry_sdk.init"), \\
     patch("rq.Worker.all", return_value=[]):
    try:
        execute_from_command_line([
            "manage.py", "slack_ai_worker_healthcheck", "--settings=settings.nestbot_healthcheck",
        ])
    except SystemExit as error:
        assert error.code == 1
""",
        ],
        env={
            **os.environ,
            "PYTHONPATH": str(Path(__file__).resolve().parents[3] / "src"),
            "DJANGO_AWS_STORAGE_BUCKET_NAME": "unit-test",
            "DJANGO_GITHUB_APP_ID": "unit-test",
            "DJANGO_GITHUB_APP_INSTALLATION_ID": "unit-test",
            "DJANGO_SENTRY_DSN": "https://unit-test@localhost/1",
            "DJANGO_SLACK_BOT_TOKEN": "xoxb-unit-test",
            "DJANGO_SLACK_SIGNING_SECRET": "unit-test",
        },
        capture_output=True,
        check=False,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "No healthy local AI queue worker" in result.stderr
