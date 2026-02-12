"""Tests for app mention event handler."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from apps.slack.events.app_mention import AppMention


class TestAppMention:
    """Test cases for AppMention event handler."""

    @pytest.fixture
    def handler(self):
        """Create AppMention handler instance."""
        return AppMention()

    @pytest.fixture
    def mock_client(self):
        """Create mock Slack client."""
        client = MagicMock()
        client.reactions_add.return_value = {"ok": True}
        client.chat_postMessage.return_value = {"ok": True}
        return client

    @pytest.fixture
    def mock_conversation(self):
        """Create mock conversation."""
        conversation = Mock()
        conversation.slack_channel_id = "C123456"
        conversation.is_nest_bot_assistant_enabled = True
        return conversation

    def test_event_type(self, handler):
        """Test that event_type is set correctly."""
        assert handler.event_type == "app_mention"

    @patch("apps.slack.events.app_mention.Conversation")
    @patch("apps.slack.events.app_mention.get_blocks")
    def test_handle_event_ai_disabled(
        self, mock_get_blocks, mock_conversation, handler, mock_client
    ):
        """Test that handler returns early when AI assistant is disabled."""
        mock_conversation.objects.filter.return_value.exists.return_value = False

        event = {
            "channel": "C123456",
            "text": "What is OWASP?",
            "ts": "1234567890.123456",
        }

        handler.handle_event(event, mock_client)

        mock_get_blocks.assert_not_called()
        mock_client.chat_postMessage.assert_not_called()

    @patch("apps.slack.events.app_mention.Conversation")
    @patch("apps.slack.events.app_mention.get_blocks")
    def test_handle_event_no_query(self, mock_get_blocks, mock_conversation, handler, mock_client):
        """Test that handler returns early when no query is found."""
        mock_conversation.objects.filter.return_value.exists.return_value = True

        event = {
            "channel": "C123456",
            "text": "",
            "ts": "1234567890.123456",
        }

        handler.handle_event(event, mock_client)

        mock_get_blocks.assert_not_called()
        mock_client.chat_postMessage.assert_not_called()

    @patch("apps.slack.events.app_mention.Conversation")
    @patch("apps.slack.events.app_mention.get_blocks")
    def test_handle_event_success(self, mock_get_blocks, mock_conversation, handler, mock_client):
        """Test successful handling of app mention event."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_get_blocks.return_value = [{"type": "section", "text": {"text": "Response"}}]

        event = {
            "channel": "C123456",
            "text": "What is OWASP?",
            "ts": "1234567890.123456",
        }

        handler.handle_event(event, mock_client)

        mock_client.reactions_add.assert_called_once_with(
            channel="C123456",
            timestamp="1234567890.123456",
            name="eyes",
        )
        mock_get_blocks.assert_called_once_with(
            query="What is OWASP?", channel_id="C123456", is_app_mention=True
        )
        mock_client.chat_postMessage.assert_called_once_with(
            channel="C123456",
            blocks=[{"type": "section", "text": {"text": "Response"}}],
            text="What is OWASP?",
            thread_ts="1234567890.123456",
        )

    @patch("apps.slack.events.app_mention.Conversation")
    @patch("apps.slack.events.app_mention.get_blocks")
    def test_handle_event_with_thread_ts(
        self, mock_get_blocks, mock_conversation, handler, mock_client
    ):
        """Test handling event with thread_ts."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_get_blocks.return_value = [{"type": "section", "text": {"text": "Response"}}]

        event = {
            "channel": "C123456",
            "text": "What is OWASP?",
            "ts": "1234567890.123456",
            "thread_ts": "1234567890.000000",
        }

        handler.handle_event(event, mock_client)

        mock_client.chat_postMessage.assert_called_once_with(
            channel="C123456",
            blocks=[{"type": "section", "text": {"text": "Response"}}],
            text="What is OWASP?",
            thread_ts="1234567890.000000",
        )

    @patch("apps.slack.events.app_mention.Conversation")
    @patch("apps.slack.events.app_mention.get_blocks")
    def test_handle_event_extract_query_from_blocks(
        self, mock_get_blocks, mock_conversation, handler, mock_client
    ):
        """Test extracting query from rich text blocks."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_get_blocks.return_value = [{"type": "section", "text": {"text": "Response"}}]

        event = {
            "channel": "C123456",
            "text": "Fallback text",
            "ts": "1234567890.123456",
            "blocks": [
                {
                    "type": "rich_text",
                    "elements": [
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {"type": "text", "text": "  What is OWASP?  "},
                            ],
                        },
                    ],
                },
            ],
        }

        handler.handle_event(event, mock_client)

        mock_get_blocks.assert_called_once_with(
            query="What is OWASP?", channel_id="C123456", is_app_mention=True
        )

    @patch("apps.slack.events.app_mention.Conversation")
    @patch("apps.slack.events.app_mention.get_blocks")
    def test_handle_event_extract_query_from_blocks_multiple_elements(
        self, mock_get_blocks, mock_conversation, handler, mock_client
    ):
        """Test extracting query from rich text blocks with multiple elements."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_get_blocks.return_value = [{"type": "section", "text": {"text": "Response"}}]

        event = {
            "channel": "C123456",
            "text": "Fallback text",
            "ts": "1234567890.123456",
            "blocks": [
                {
                    "type": "rich_text",
                    "elements": [
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {"type": "user", "user_id": "U123"},
                                {"type": "text", "text": "What is OWASP?"},
                            ],
                        },
                    ],
                },
            ],
        }

        handler.handle_event(event, mock_client)

        mock_get_blocks.assert_called_once_with(
            query="What is OWASP?", channel_id="C123456", is_app_mention=True
        )

    @patch("apps.slack.events.app_mention.Conversation")
    @patch("apps.slack.events.app_mention.get_blocks")
    def test_handle_event_blocks_not_rich_text(
        self, mock_get_blocks, mock_conversation, handler, mock_client
    ):
        """Test that non-rich_text blocks don't extract query."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_get_blocks.return_value = [{"type": "section", "text": {"text": "Response"}}]

        event = {
            "channel": "C123456",
            "text": "What is OWASP?",
            "ts": "1234567890.123456",
            "blocks": [
                {
                    "type": "section",
                    "text": {"text": "Some other block"},
                },
            ],
        }

        handler.handle_event(event, mock_client)

        mock_get_blocks.assert_called_once_with(
            query="What is OWASP?", channel_id="C123456", is_app_mention=True
        )

    @patch("apps.slack.events.app_mention.Conversation")
    @patch("apps.slack.events.app_mention.get_blocks")
    def test_handle_event_reaction_already_exists(
        self, mock_get_blocks, mock_conversation, handler, mock_client
    ):
        """Test handling when reaction already exists."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_get_blocks.return_value = [{"type": "section", "text": {"text": "Response"}}]
        mock_client.reactions_add.return_value = {"ok": False, "error": "already_reacted"}

        event = {
            "channel": "C123456",
            "text": "What is OWASP?",
            "ts": "1234567890.123456",
        }

        handler.handle_event(event, mock_client)

        mock_client.reactions_add.assert_called_once()
        mock_get_blocks.assert_called_once()

    @patch("apps.slack.events.app_mention.Conversation")
    @patch("apps.slack.events.app_mention.get_blocks")
    def test_handle_event_reaction_error(
        self, mock_get_blocks, mock_conversation, handler, mock_client
    ):
        """Test handling when reaction fails with error."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_get_blocks.return_value = [{"type": "section", "text": {"text": "Response"}}]
        mock_client.reactions_add.return_value = {"ok": False, "error": "invalid_name"}

        event = {
            "channel": "C123456",
            "text": "What is OWASP?",
            "ts": "1234567890.123456",
        }

        handler.handle_event(event, mock_client)

        mock_client.reactions_add.assert_called_once()
        mock_get_blocks.assert_called_once()

    @patch("apps.slack.events.app_mention.Conversation")
    @patch("apps.slack.events.app_mention.get_blocks")
    def test_handle_event_reaction_exception(
        self, mock_get_blocks, mock_conversation, handler, mock_client
    ):
        """Test handling when reaction raises exception."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_get_blocks.return_value = [{"type": "section", "text": {"text": "Response"}}]
        mock_client.reactions_add.side_effect = Exception("Network error")

        event = {
            "channel": "C123456",
            "text": "What is OWASP?",
            "ts": "1234567890.123456",
        }

        handler.handle_event(event, mock_client)

        mock_client.reactions_add.assert_called_once()
        mock_get_blocks.assert_called_once()
        mock_client.chat_postMessage.assert_called_once()
