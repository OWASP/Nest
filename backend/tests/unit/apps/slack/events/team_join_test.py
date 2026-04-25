from unittest.mock import Mock

import pytest

from apps.slack.events.team_join import TeamJoin


class TestTeamJoinHandler:
    @pytest.fixture
    def mock_slack_config(self, mocker):
        mock_app = Mock()
        mocker.patch("apps.slack.apps.SlackConfig.app", mock_app)
        return mock_app

    def test_handle_event_user_joined(self):
        mock_client = Mock()
        mock_conversation = {"channel": {"id": "C67890"}}
        mock_client.conversations_open.return_value = mock_conversation

        handler = TeamJoin()
        handler.open_conversation = Mock(return_value=mock_conversation)
        handler.handle_event({"user": {"id": "U12345"}}, mock_client)

        handler.open_conversation.assert_called_once_with(mock_client, "U12345")
        mock_client.chat_postMessage.assert_called_once()
        call_args = mock_client.chat_postMessage.call_args[1]

        assert call_args["channel"] == "C67890"
        assert "blocks" in call_args
        assert "text" in call_args

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
