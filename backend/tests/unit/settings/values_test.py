import os

import pytest
from configurations import values

from settings.values import OptionalSecretValue

TEST_TOKEN = "xoxb-test-token"  # noqa: S105


class TestOptionalSecretValue:
    def test_inherits_from_secret_value(self):
        assert issubclass(OptionalSecretValue, values.SecretValue)

    @pytest.fixture(autouse=True)
    def clear_slack_env(self):
        for key in ("DJANGO_SLACK_BOT_TOKEN", "DJANGO_SLACK_SIGNING_SECRET"):
            os.environ.pop(key, None)
        yield
        for key in ("DJANGO_SLACK_BOT_TOKEN", "DJANGO_SLACK_SIGNING_SECRET"):
            os.environ.pop(key, None)

    def test_returns_empty_when_unset(self):
        assert OptionalSecretValue().setup("SLACK_BOT_TOKEN") == ""

    def test_returns_empty_when_env_is_blank(self):
        os.environ["DJANGO_SLACK_BOT_TOKEN"] = ""
        assert OptionalSecretValue().setup("SLACK_BOT_TOKEN") == ""

    def test_reads_value_from_environment(self):
        os.environ["DJANGO_SLACK_BOT_TOKEN"] = TEST_TOKEN
        assert OptionalSecretValue().setup("SLACK_BOT_TOKEN") == TEST_TOKEN

    def test_ignores_environment_when_environ_disabled(self):
        os.environ["DJANGO_SLACK_BOT_TOKEN"] = TEST_TOKEN
        assert OptionalSecretValue(environ=False).setup("SLACK_BOT_TOKEN") == ""
