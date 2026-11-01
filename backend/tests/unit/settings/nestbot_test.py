"""Check Slack routing with fresh Django configuration imports."""

import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    ("module", "configuration", "slack_enabled"),
    [
        ("settings.nestbot", "Staging", True),
        ("settings.staging", "Staging", False),
        ("settings.production", "Production", True),
    ],
)
def test_slack_configuration(module, configuration, slack_enabled):
    # SlackConfig and urlpatterns are initialized at import time; use a fresh process.
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
        ],
        env={
            **os.environ,
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
