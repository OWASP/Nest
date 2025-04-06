from unittest.mock import MagicMock, patch

import pytest

from apps.slack.apps import SlackConfig
from apps.slack.constants import OWASP_CONTRIBUTE_CHANNEL_ID, OWASP_GSOC_CHANNEL_ID
from apps.slack.events.member_joined_channel.catch_all import catch_all_handler


class TestCatchAllEventHandler:
    @pytest.fixture
    def mock_slack_event(self):
        return {"user": "U123456", "channel": "C123456"}

    def test_handler_calls_ack(self, mock_slack_event):
        mock_ack = MagicMock()
        mock_client = MagicMock()

        catch_all_handler(event=mock_slack_event, client=mock_client, ack=mock_ack)

        mock_ack.assert_called_once()

    @patch("apps.slack.apps.SlackConfig.app")
    def test_event_registration(self, mock_app):
        SlackConfig.app = mock_app

        import importlib

        import apps.slack.events.member_joined_channel.catch_all

        importlib.reload(apps.slack.events.member_joined_channel.catch_all)

        mock_app.event.assert_called_once()
        call_args = mock_app.event.call_args
        assert call_args[0][0] == "member_joined_channel"

        matcher_func = call_args[1]["matchers"][0]

        assert matcher_func({"channel": "C999999"})

        assert not matcher_func({"channel": OWASP_CONTRIBUTE_CHANNEL_ID.lstrip("#")})
        assert not matcher_func({"channel": OWASP_GSOC_CHANNEL_ID.lstrip("#")})

    def test_handler_with_different_params(self):
        mock_ack = MagicMock()

        catch_all_handler(event={"channel": "C123456"}, client=MagicMock(), ack=mock_ack)

        mock_ack.assert_called_once()

        mock_ack.reset_mock()
        catch_all_handler({}, None, mock_ack)
        mock_ack.assert_called_once()
