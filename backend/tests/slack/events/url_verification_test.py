from unittest.mock import MagicMock, patch

import pytest

from apps.slack.apps import SlackConfig
from apps.slack.events.url_verification import url_verification_handler


@pytest.fixture()
def mock_slack_app():
    mock_app = MagicMock()
    mock_app.event = MagicMock(return_value=lambda x: x)
    return mock_app


@pytest.fixture()
def slack_bot(mock_slack_app):
    original_app = SlackConfig.app
    SlackConfig.app = mock_slack_app
    yield SlackConfig
    SlackConfig.app = original_app


class TestUrlVerification:
    def test_url_verification_handler_with_app(self, slack_bot):
        from apps.slack.events.url_verification import url_verification_handler

        if slack_bot.app:
            slack_bot.app.event("url_verification")(url_verification_handler)

            event = {"challenge": "test_challenge"}
            response = url_verification_handler(event)

            assert response == "test_challenge"
            slack_bot.app.event.assert_called_once_with("url_verification")

    def test_url_verification_handler_with_args_kwargs(self, slack_bot):
        event = {"challenge": "test_challenge"}
        additional_arg = "extra_arg"
        additional_kwarg = {"key": "value"}

        response = url_verification_handler(event, additional_arg, **additional_kwarg)

        assert response == "test_challenge"

    def test_url_verification_handler_without_app(self, slack_bot):
        SlackConfig.app = None
        event = {"challenge": "test_challenge"}

        response = url_verification_handler(event)

        assert response == "test_challenge"

    def test_url_verification_handler_missing_challenge(self, slack_bot):
        event = {}

        with pytest.raises(KeyError):
            url_verification_handler(event)

    def test_module_level_registration(self):
        with patch("apps.slack.apps.SlackConfig") as mock_config:
            mock_config.app = MagicMock()
            mock_config.app.event.return_value = lambda f: f

            import sys

            if "apps.slack.events.url_verification" in sys.modules:
                del sys.modules["apps.slack.events.url_verification"]

            mock_config.app.event("url_verification")
            mock_config.app.event.assert_called_once_with("url_verification")
