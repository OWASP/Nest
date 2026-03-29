"""Tests for app mention event handler."""

from unittest.mock import MagicMock, Mock, patch

import pytest
from slack_sdk.errors import SlackApiError

from apps.slack.events.app_mention import AppMention
from apps.slack.services.message_auto_reply import process_ai_query_async


def _assert_ai_enqueued(mock_django_rq, **expected):
    mock_django_rq.get_queue.assert_called_once_with("ai")
    mock_queue = mock_django_rq.get_queue.return_value
    mock_queue.enqueue.assert_called_once()
    args, kwargs = mock_queue.enqueue.call_args
    assert args[0] is process_ai_query_async
    for key, value in expected.items():
        assert kwargs.get(key) == value


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

    @patch("apps.slack.events.app_mention.django_rq")
    @patch("apps.slack.events.app_mention.Conversation")
    def test_handle_event_ai_disabled(
        self, mock_conversation, mock_django_rq, handler, mock_client
    ):
        """Test that handler returns early when AI assistant is disabled."""
        mock_conversation.objects.filter.return_value.exists.return_value = False

        event = {
            "channel": "C123456",
            "text": "What is OWASP?",
            "ts": "1234567890.123456",
        }

        handler.handle_event(event, mock_client)

        mock_django_rq.get_queue.assert_not_called()
        mock_client.chat_postMessage.assert_not_called()

    @patch("apps.slack.events.app_mention.django_rq")
    @patch("apps.slack.events.app_mention.Conversation")
    def test_handle_event_filters_unsupported_mimetypes(
        self, mock_conversation, mock_django_rq, handler, mock_client
    ):
        """Test that files with unsupported MIME types are not enqueued as images."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_queue = Mock()
        mock_django_rq.get_queue.return_value = mock_queue

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

        _assert_ai_enqueued(
            mock_django_rq,
            query="Check this file",
            channel_id="C123456",
            message_ts="1234567890.123456",
            thread_ts="1234567890.123456",
            is_app_mention=True,
            slack_image_files=None,
        )

    @patch("apps.slack.events.app_mention.django_rq")
    @patch("apps.slack.events.app_mention.Conversation")
    def test_handle_event_filters_oversized_images(
        self, mock_conversation, mock_django_rq, handler, mock_client
    ):
        """Test that images exceeding MAX_IMAGE_SIZE are not enqueued."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_django_rq.get_queue.return_value = Mock()

        event = {
            "channel": "C123456",
            "text": "Check this image",
            "ts": "1234567890.123456",
            "files": [
                {
                    "mimetype": "image/png",
                    "size": 3 * 1024 * 1024,
                    "url_private": "https://files.slack.com/big.png",
                },
            ],
        }

        handler.handle_event(event, mock_client)

        _assert_ai_enqueued(
            mock_django_rq,
            query="Check this image",
            channel_id="C123456",
            message_ts="1234567890.123456",
            thread_ts="1234567890.123456",
            is_app_mention=True,
            slack_image_files=None,
        )

    @patch("apps.slack.events.app_mention.django_rq")
    @patch("apps.slack.events.app_mention.Conversation")
    def test_handle_event_no_query(self, mock_conversation, mock_django_rq, handler, mock_client):
        """Test that handler returns early when no query is found."""
        mock_conversation.objects.filter.return_value.exists.return_value = True

        event = {
            "channel": "C123456",
            "text": "",
            "ts": "1234567890.123456",
        }

        handler.handle_event(event, mock_client)

        mock_django_rq.get_queue.assert_not_called()
        mock_client.chat_postMessage.assert_not_called()

    @patch("apps.slack.events.app_mention.django_rq")
    @patch("apps.slack.events.app_mention.Conversation")
    def test_handle_event_extract_query_from_blocks(
        self, mock_conversation, mock_django_rq, handler, mock_client
    ):
        """Test extracting query from rich text blocks."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_django_rq.get_queue.return_value = Mock()

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

        _assert_ai_enqueued(
            mock_django_rq,
            query="What is OWASP?",
            channel_id="C123456",
            message_ts="1234567890.123456",
            thread_ts="1234567890.123456",
            is_app_mention=True,
            slack_image_files=None,
        )

    @patch("apps.slack.events.app_mention.django_rq")
    @patch("apps.slack.events.app_mention.Conversation")
    def test_handle_event_extract_query_from_blocks_multiple_elements(
        self, mock_conversation, mock_django_rq, handler, mock_client
    ):
        """Test extracting query from rich text blocks with multiple elements."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_django_rq.get_queue.return_value = Mock()

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

        _assert_ai_enqueued(
            mock_django_rq,
            query="What is OWASP?",
            channel_id="C123456",
            message_ts="1234567890.123456",
            thread_ts="1234567890.123456",
            is_app_mention=True,
            slack_image_files=None,
        )

    @patch("apps.slack.events.app_mention.django_rq")
    @patch("apps.slack.events.app_mention.Conversation")
    def test_handle_event_blocks_without_text_element(
        self, mock_conversation, mock_django_rq, handler, mock_client
    ):
        """Test handle_event with blocks but no text elements falls back to event text."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_django_rq.get_queue.return_value = Mock()

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
                            "elements": [{"type": "user", "user_id": "U123"}],
                        },
                    ],
                },
            ],
        }

        handler.handle_event(event, mock_client)

        _assert_ai_enqueued(
            mock_django_rq,
            query="Fallback text",
            channel_id="C123456",
            message_ts="1234567890.123456",
            thread_ts="1234567890.123456",
            is_app_mention=True,
            slack_image_files=None,
        )

    @patch("apps.slack.events.app_mention.django_rq")
    @patch("apps.slack.events.app_mention.Conversation")
    def test_handle_event_blocks_without_rich_text_section(
        self, mock_conversation, mock_django_rq, handler, mock_client
    ):
        """Test handle_event with blocks but no rich_text_section."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_django_rq.get_queue.return_value = Mock()

        event = {
            "channel": "C123456",
            "text": "Fallback text",
            "ts": "1234567890.123456",
            "blocks": [
                {
                    "type": "rich_text",
                    "elements": [{"type": "other_type", "data": "something"}],
                },
            ],
        }

        handler.handle_event(event, mock_client)

        _assert_ai_enqueued(
            mock_django_rq,
            query="Fallback text",
            channel_id="C123456",
            message_ts="1234567890.123456",
            thread_ts="1234567890.123456",
            is_app_mention=True,
            slack_image_files=None,
        )

    @patch("apps.slack.events.app_mention.django_rq")
    @patch("apps.slack.events.app_mention.Conversation")
    def test_handle_event_blocks_not_rich_text(
        self, mock_conversation, mock_django_rq, handler, mock_client
    ):
        """Test that non-rich_text blocks don't extract query."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_django_rq.get_queue.return_value = Mock()

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

        _assert_ai_enqueued(
            mock_django_rq,
            query="What is OWASP?",
            channel_id="C123456",
            message_ts="1234567890.123456",
            thread_ts="1234567890.123456",
            is_app_mention=True,
            slack_image_files=None,
        )

    @patch("apps.slack.events.app_mention.django_rq")
    @patch("apps.slack.events.app_mention.Conversation")
    def test_handle_event_reaction_already_exists(
        self, mock_conversation, mock_django_rq, handler, mock_client
    ):
        """Test handling when reaction already exists (SlackApiError)."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_django_rq.get_queue.return_value = Mock()
        mock_client.reactions_add.side_effect = SlackApiError(
            message="already_reacted",
            response={"ok": False, "error": "already_reacted"},
        )

        event = {
            "channel": "C123456",
            "text": "What is OWASP?",
            "ts": "1234567890.123456",
        }

        handler.handle_event(event, mock_client)

        mock_client.reactions_add.assert_called_once()
        _assert_ai_enqueued(
            mock_django_rq,
            query="What is OWASP?",
            channel_id="C123456",
            message_ts="1234567890.123456",
            thread_ts="1234567890.123456",
            is_app_mention=True,
            slack_image_files=None,
        )

    @patch("apps.slack.events.app_mention.django_rq")
    @patch("apps.slack.events.app_mention.Conversation")
    def test_handle_event_reaction_error(
        self, mock_conversation, mock_django_rq, handler, mock_client
    ):
        """Test handling when reaction fails with a non-already_reacted Slack error."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_django_rq.get_queue.return_value = Mock()
        mock_client.reactions_add.side_effect = SlackApiError(
            message="invalid_name",
            response={"ok": False, "error": "invalid_name"},
        )

        event = {
            "channel": "C123456",
            "text": "What is OWASP?",
            "ts": "1234567890.123456",
        }

        handler.handle_event(event, mock_client)

        mock_client.reactions_add.assert_called_once()
        _assert_ai_enqueued(
            mock_django_rq,
            query="What is OWASP?",
            channel_id="C123456",
            message_ts="1234567890.123456",
            thread_ts="1234567890.123456",
            is_app_mention=True,
            slack_image_files=None,
        )

    @patch("apps.slack.events.app_mention.django_rq")
    @patch("apps.slack.events.app_mention.Conversation")
    def test_handle_event_reaction_exception(
        self, mock_conversation, mock_django_rq, handler, mock_client
    ):
        """Test that non-SlackApiError from reactions_add aborts before enqueue."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_django_rq.get_queue.return_value = Mock()
        mock_client.reactions_add.side_effect = RuntimeError("Network error")

        event = {
            "channel": "C123456",
            "text": "What is OWASP?",
            "ts": "1234567890.123456",
        }

        with pytest.raises(RuntimeError, match="Network error"):
            handler.handle_event(event, mock_client)

        mock_django_rq.get_queue.assert_not_called()
        mock_client.chat_postMessage.assert_not_called()

    @patch("apps.slack.events.app_mention.django_rq")
    @patch("apps.slack.events.app_mention.Conversation")
    def test_handle_event_with_image_files(
        self, mock_conversation, mock_django_rq, handler, mock_client
    ):
        """Test that image metadata is enqueued for the worker (no download in handler)."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_django_rq.get_queue.return_value = Mock()

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

        _assert_ai_enqueued(
            mock_django_rq,
            query="What is in this image?",
            channel_id="C123456",
            message_ts="1234567890.123456",
            thread_ts="1234567890.123456",
            is_app_mention=True,
            slack_image_files=[
                {"url_private": "https://files.slack.com/image.png", "mimetype": "image/png"},
            ],
        )

    @patch("apps.slack.events.app_mention.django_rq")
    @patch("apps.slack.events.app_mention.Conversation")
    def test_handle_event_image_without_url_private(
        self, mock_conversation, mock_django_rq, handler, mock_client
    ):
        """Test that images missing url_private are omitted from slack_image_files."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_django_rq.get_queue.return_value = Mock()

        event = {
            "channel": "C123456",
            "text": "What is in this image?",
            "ts": "1234567890.123456",
            "files": [
                {
                    "mimetype": "image/jpeg",
                    "size": 500,
                },
            ],
        }

        handler.handle_event(event, mock_client)

        _assert_ai_enqueued(
            mock_django_rq,
            query="What is in this image?",
            channel_id="C123456",
            message_ts="1234567890.123456",
            thread_ts="1234567890.123456",
            is_app_mention=True,
            slack_image_files=None,
        )

    @patch("apps.slack.events.app_mention.django_rq")
    @patch("apps.slack.events.app_mention.Conversation")
    def test_handle_event_success(self, mock_conversation, mock_django_rq, handler, mock_client):
        """Test successful handling enqueues async processing."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_django_rq.get_queue.return_value = Mock()

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
        _assert_ai_enqueued(
            mock_django_rq,
            query="What is OWASP?",
            channel_id="C123456",
            message_ts="1234567890.123456",
            thread_ts="1234567890.123456",
            is_app_mention=True,
            slack_image_files=None,
        )
        mock_client.chat_postMessage.assert_not_called()

    @patch("apps.slack.events.app_mention.django_rq")
    @patch("apps.slack.events.app_mention.Conversation")
    def test_handle_event_with_thread_ts(
        self, mock_conversation, mock_django_rq, handler, mock_client
    ):
        """Test thread_ts is passed to the enqueued job."""
        mock_conversation.objects.filter.return_value.exists.return_value = True
        mock_django_rq.get_queue.return_value = Mock()

        event = {
            "channel": "C123456",
            "text": "What is OWASP?",
            "ts": "1234567890.123456",
            "thread_ts": "1234567890.000000",
        }

        handler.handle_event(event, mock_client)

        _assert_ai_enqueued(
            mock_django_rq,
            query="What is OWASP?",
            channel_id="C123456",
            message_ts="1234567890.123456",
            thread_ts="1234567890.000000",
            is_app_mention=True,
            slack_image_files=None,
        )
        mock_client.chat_postMessage.assert_not_called()
