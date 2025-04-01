from unittest.mock import MagicMock, Mock, patch

import pytest
from slack_sdk.errors import SlackApiError

from apps.slack.events.team_join import team_join_handler


class TestSlackHandler:
    @pytest.fixture()
    def mock_slack_config(self, mocker):
        mock_app = Mock()
        mocker.patch("apps.slack.apps.SlackConfig.app", mock_app)
        return mock_app

    def test_handler_user_joined(self):
        mock_ack = Mock()
        mock_client = Mock()
        mock_conversation = {"channel": {"id": "C67890"}}
        mock_client.conversations_open.return_value = mock_conversation

        with patch("time.sleep", return_value=None):
            team_join_handler({"user": {"id": "U12345"}}, mock_client, mock_ack)

        mock_ack.assert_called_once()
        mock_client.conversations_open.assert_called_once_with(users="U12345")
        mock_client.chat_postMessage.assert_called_once()

        call_args = mock_client.chat_postMessage.call_args[1]

        assert call_args["channel"] == "C67890"
        assert "blocks" in call_args

        blocks = call_args["blocks"]

        block_texts = [
            block["text"]["text"]
            for block in blocks
            if block["type"] == "section" and "text" in block
        ]

        assert any("*Welcome to the OWASP Slack Community" in text for text in block_texts)
        assert any("OWASP Nest" in text for text in block_texts)
        assert any("#chapter-<name>" in text for text in block_texts)
        assert any("<#C255XSY04>" in text for text in block_texts)
        assert any("We're here to support your journey" in text for text in block_texts)

    @patch("apps.slack.events.team_join.settings.SLACK_EVENTS_ENABLED", new=False)
    def test_handler_events_disabled(self):
        mock_ack = Mock()
        mock_client = Mock()

        team_join_handler({"user": {"id": "U12345"}}, mock_client, mock_ack)

        mock_ack.assert_called_once()
        mock_client.conversations_open.assert_not_called()
        mock_client.chat_postMessage.assert_not_called()

    def test_handler_cannot_dm_bot(self):
        mock_ack = Mock()
        mock_client = Mock()
        mock_error_response = {"error": "cannot_dm_bot"}
        mock_client.conversations_open.side_effect = SlackApiError(
            "Cannot DM bot", mock_error_response
        )
        mock_client.users_info.return_value = {"user": {"name": "bot_user"}}

        team_join_handler({"user": {"id": "B12345"}}, mock_client, mock_ack)

        mock_ack.assert_called_once()
        mock_client.conversations_open.assert_called_once_with(users="B12345")
        mock_client.chat_postMessage.assert_not_called()
        mock_client.users_info.assert_not_called()

    def test_handler_other_slack_error(self):
        mock_ack = Mock()
        mock_client = Mock()
        mock_error_response = {"error": "other_error"}
        mock_client.conversations_open.side_effect = SlackApiError(
            "Other error", mock_error_response
        )
        mock_client.users_info.return_value = {"user": {"name": "problem_user"}}

        with pytest.raises(SlackApiError):
            team_join_handler({"user": {"id": "U12345"}}, mock_client, mock_ack)

        mock_ack.assert_called_once()
        mock_client.conversations_open.assert_called_once_with(users="U12345")
        mock_client.users_info.assert_called_once_with(user="U12345")

    @patch("apps.slack.apps.SlackConfig.app")
    def test_event_registration(self, mock_app):
        event_decorator = MagicMock(return_value=lambda func: func)
        mock_app.event.return_value = event_decorator

        import importlib

        from apps.slack.events import team_join

        importlib.reload(team_join)

        mock_app.event.assert_called_once_with("team_join")
