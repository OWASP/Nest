from unittest.mock import MagicMock

import pytest

from apps.slack.apps import SlackConfig
from apps.slack.events.url_verification import url_verification_handler


@pytest.fixture
def mock_slack_app():
    mock_app = MagicMock()
    mock_app.event = MagicMock()
    return mock_app


@pytest.fixture
def slack_bot(mock_slack_app):
    SlackConfig.app = mock_slack_app
    return SlackConfig


class TestUrlVerification:
    def test_url_verification_handler(self, slack_bot):
        event = {"challenge": "test_challenge"}

        response = url_verification_handler(event)

        assert response == "test_challenge"
