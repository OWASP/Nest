"""Tests for AI command functionality."""

from unittest.mock import Mock, patch

import pytest

from apps.slack.commands.ai import Ai
from apps.slack.commands.command import CommandBase
from apps.slack.services.message_auto_reply import process_ai_query_async


class TestAiCommand:
    """Test cases for AI command functionality."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test data before each test method."""
        self.ai_command = Ai()

    @patch("apps.slack.commands.ai.settings")
    @patch("apps.slack.commands.ai.django_rq")
    def test_handler_enqueues_job(self, mock_django_rq, mock_settings):
        """Test /ai enqueues background processing."""
        mock_settings.SLACK_COMMANDS_ENABLED = True
        mock_queue = Mock()
        mock_django_rq.get_queue.return_value = mock_queue

        ack = Mock()
        client = Mock()
        command = {
            "text": "What is OWASP?",
            "user_id": "U123456",
            "channel_id": "C123456",
        }

        self.ai_command.handler(ack, command, client)

        ack.assert_called_once()
        mock_django_rq.get_queue.assert_called_once_with("ai")
        mock_queue.enqueue.assert_called_once()
        args, kwargs = mock_queue.enqueue.call_args
        assert args[0] is process_ai_query_async
        assert kwargs == {
            "query": "What is OWASP?",
            "channel_id": "C123456",
            "message_ts": None,
            "thread_ts": None,
            "is_app_mention": False,
            "user_id": "U123456",
        }

    @patch("apps.slack.commands.ai.settings")
    @patch("apps.slack.commands.ai.django_rq")
    def test_handler_strips_whitespace_query(self, mock_django_rq, mock_settings):
        """Test query text is stripped before enqueue."""
        mock_settings.SLACK_COMMANDS_ENABLED = True
        mock_queue = Mock()
        mock_django_rq.get_queue.return_value = mock_queue

        ack = Mock()
        client = Mock()
        command = {
            "text": "  What is OWASP security?  ",
            "user_id": "U123456",
            "channel_id": "C123456",
        }

        self.ai_command.handler(ack, command, client)

        _, kwargs = mock_queue.enqueue.call_args
        assert kwargs["query"] == "What is OWASP security?"

    @patch("apps.slack.commands.ai.settings")
    @patch("apps.slack.commands.ai.django_rq")
    def test_handler_empty_text_posts_usage_ephemeral(self, mock_django_rq, mock_settings):
        """Test empty /ai text posts usage hint and does not enqueue."""
        mock_settings.SLACK_COMMANDS_ENABLED = True

        ack = Mock()
        client = Mock()
        command = {"text": "", "user_id": "U123456", "channel_id": "C123456"}

        self.ai_command.handler(ack, command, client)

        ack.assert_called_once()
        mock_django_rq.get_queue.assert_not_called()
        client.chat_postEphemeral.assert_called_once()
        assert "Usage" in client.chat_postEphemeral.call_args.kwargs["text"]

    @patch("apps.slack.commands.ai.settings")
    @patch("apps.slack.commands.ai.django_rq")
    def test_handler_whitespace_only_posts_usage_ephemeral(self, mock_django_rq, mock_settings):
        """Test whitespace-only text is treated as empty."""
        mock_settings.SLACK_COMMANDS_ENABLED = True

        ack = Mock()
        client = Mock()
        command = {"text": "   ", "user_id": "U123456", "channel_id": "C123456"}

        self.ai_command.handler(ack, command, client)

        mock_django_rq.get_queue.assert_not_called()
        client.chat_postEphemeral.assert_called_once()

    @patch("apps.slack.commands.ai.settings")
    @patch("apps.slack.commands.ai.django_rq")
    def test_handler_commands_disabled(self, mock_django_rq, mock_settings):
        """Test SLACK_COMMANDS_ENABLED False skips enqueue and ephemeral."""
        mock_settings.SLACK_COMMANDS_ENABLED = False

        ack = Mock()
        client = Mock()
        command = {"text": "What is OWASP?", "user_id": "U1", "channel_id": "C1"}

        self.ai_command.handler(ack, command, client)

        ack.assert_called_once()
        mock_django_rq.get_queue.assert_not_called()
        client.chat_postEphemeral.assert_not_called()

    @patch("apps.slack.commands.ai.settings")
    @patch("apps.slack.commands.ai.django_rq")
    def test_handler_enqueue_failure_posts_error_ephemeral(self, mock_django_rq, mock_settings):
        """Test enqueue failure posts error ephemeral and does not propagate."""
        mock_settings.SLACK_COMMANDS_ENABLED = True
        mock_django_rq.get_queue.return_value.enqueue.side_effect = RuntimeError("queue down")

        ack = Mock()
        client = Mock()
        command = {"text": "What is OWASP?", "user_id": "U1", "channel_id": "C1"}

        self.ai_command.handler(ack, command, client)

        ack.assert_called_once()
        client.chat_postEphemeral.assert_called_once_with(
            channel="C1",
            user="U1",
            text=("⚠️ An error occurred while processing your query. Please try again later."),
        )

    def test_ai_command_inheritance(self):
        """Test that Ai command inherits from CommandBase."""
        ai_command = Ai()
        assert isinstance(ai_command, CommandBase)

    @patch("apps.slack.commands.ai.settings")
    @patch("apps.slack.commands.ai.django_rq")
    def test_handler_preserves_special_characters_in_query(self, mock_django_rq, mock_settings):
        """Test special characters in query are passed through."""
        mock_settings.SLACK_COMMANDS_ENABLED = True
        mock_queue = Mock()
        mock_django_rq.get_queue.return_value = mock_queue

        ack = Mock()
        client = Mock()
        q = "What is XSS & SQL injection? How to prevent <script> attacks?"
        command = {"text": q, "user_id": "U123456", "channel_id": "C123456"}

        self.ai_command.handler(ack, command, client)

        _, kwargs = mock_queue.enqueue.call_args
        assert kwargs["query"] == q
