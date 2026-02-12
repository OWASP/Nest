"""Tests for app mention event handler."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from apps.slack.events.app_mention import AppMention

TEST_BOT_TOKEN = "xoxb-test-token"  # noqa: S105


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

    @patch("apps.slack.events.app_mention.download_file")
    @patch("apps.slack.events.app_mention.Conversation")
    @patch("apps.slack.events.app_mention.get_blocks")
    def test_handle_event_filters_unsupported_mimetypes(
        self, mock_get_blocks, mock_conversation, mock_download_file, handler, mock_client
    ):
        """Test that files with unsupported MIME types are filtered out."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_get_blocks.return_value = [{"type": "section", "text": {"text": "Response"}}]
        mock_client.token = TEST_BOT_TOKEN

        event = {
            "channel": "C123456",
            "text": "Check this file",
            "ts": "1234567890.123456",
            "files": [
                {
                    "mimetype": "application/pdf",
                    "size": 1024,
                    "url_private": "https://files.slack.com/doc.pdf",
                },
            ],
        }

        handler.handle_event(event, mock_client)

        mock_download_file.assert_not_called()
        call_kwargs = mock_get_blocks.call_args.kwargs
        assert call_kwargs["images"] == []

    @patch("apps.slack.events.app_mention.download_file")
    @patch("apps.slack.events.app_mention.Conversation")
    @patch("apps.slack.events.app_mention.get_blocks")
    def test_handle_event_filters_oversized_images(
        self, mock_get_blocks, mock_conversation, mock_download_file, handler, mock_client
    ):
        """Test that images exceeding MAX_IMAGE_SIZE are filtered out."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_get_blocks.return_value = [{"type": "section", "text": {"text": "Response"}}]
        mock_client.token = TEST_BOT_TOKEN

        event = {
            "channel": "C123456",
            "text": "Check this image",
            "ts": "1234567890.123456",
            "files": [
                {
                    "mimetype": "image/png",
                    "size": 3 * 1024 * 1024,  # 3MB, exceeds 2MB limit
                    "url_private": "https://files.slack.com/big.png",
                },
            ],
        }

        handler.handle_event(event, mock_client)

        mock_download_file.assert_not_called()
        call_kwargs = mock_get_blocks.call_args.kwargs
        assert call_kwargs["images"] == []

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
            query="What is OWASP?", images=[], channel_id="C123456", is_app_mention=True
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
            query="What is OWASP?", images=[], channel_id="C123456", is_app_mention=True
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
            query="What is OWASP?", images=[], channel_id="C123456", is_app_mention=True
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

    @patch("apps.slack.events.app_mention.download_file")
    @patch("apps.slack.events.app_mention.Conversation")
    @patch("apps.slack.events.app_mention.get_blocks")
    def test_handle_event_with_image_files(
        self, mock_get_blocks, mock_conversation, mock_download_file, handler, mock_client
    ):
        """Test that image files are downloaded, base64 encoded, and passed to get_blocks."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_get_blocks.return_value = [{"type": "section", "text": {"text": "Response"}}]
        mock_download_file.return_value = b"\x89PNG\r\n"
        mock_client.token = TEST_BOT_TOKEN

        event = {
            "channel": "C123456",
            "text": "What is in this image?",
            "ts": "1234567890.123456",
            "files": [
                {
                    "mimetype": "image/png",
                    "size": 1024,
                    "url_private": "https://files.slack.com/image.png",
                },
            ],
        }

        handler.handle_event(event, mock_client)

        mock_download_file.assert_called_once_with(
            "https://files.slack.com/image.png", TEST_BOT_TOKEN
        )
        call_kwargs = mock_get_blocks.call_args.kwargs
        assert len(call_kwargs["images"]) == 1
        assert call_kwargs["images"][0].startswith("data:image/png;base64,")

    @patch("apps.slack.events.app_mention.download_file")
    @patch("apps.slack.events.app_mention.Conversation")
    @patch("apps.slack.events.app_mention.get_blocks")
    def test_handle_event_image_download_failure(
        self, mock_get_blocks, mock_conversation, mock_download_file, handler, mock_client
    ):
        """Test that failed image downloads are skipped gracefully."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_get_blocks.return_value = [{"type": "section", "text": {"text": "Response"}}]
        mock_download_file.return_value = None
        mock_client.token = TEST_BOT_TOKEN

        event = {
            "channel": "C123456",
            "text": "What is in this image?",
            "ts": "1234567890.123456",
            "files": [
                {
                    "mimetype": "image/jpeg",
                    "size": 500,
                    "url_private": "https://files.slack.com/broken.jpg",
                },
            ],
        }

        handler.handle_event(event, mock_client)

        mock_download_file.assert_called_once()
        call_kwargs = mock_get_blocks.call_args.kwargs
        assert call_kwargs["images"] == []

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
            query="What is OWASP?", images=[], channel_id="C123456", is_app_mention=True
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
