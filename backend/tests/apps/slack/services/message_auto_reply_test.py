"""Tests for message auto reply service."""

from unittest.mock import Mock, patch

import pytest
from slack_sdk.errors import SlackApiError

from apps.slack.apps import SlackConfig
from apps.slack.models import Conversation, Message, Workspace
from apps.slack.services.message_auto_reply import (
    ERROR_UNABLE_TO_GENERATE_RESPONSE,
    generate_ai_reply_if_unanswered,
)
from apps.slack.utils import format_ai_response_for_slack, truncate_for_slack_fallback

TEST_BOT_TOKEN = "xoxb-test-token"  # noqa: S105


class TestMessageAutoReply:
    """Test cases for message auto reply functionality."""

    @pytest.fixture
    def mock_workspace(self):
        """Mock workspace object."""
        workspace = Mock(spec=Workspace)
        workspace.slack_workspace_id = "T123456"
        workspace.bot_token = TEST_BOT_TOKEN
        return workspace

    @pytest.fixture
    def mock_conversation(self, mock_workspace):
        """Mock conversation object."""
        conversation = Mock(spec=Conversation)
        conversation.slack_channel_id = "C123456"
        conversation.workspace = mock_workspace
        conversation.is_nest_bot_assistant_enabled = True
        return conversation

    @pytest.fixture
    def mock_message(self, mock_conversation):
        """Mock message object."""
        message = Mock(spec=Message)
        message.id = 1
        message.slack_message_id = "1234567890.123456"
        message.text = "What is OWASP?"
        message.conversation = mock_conversation
        return message

    @patch.object(SlackConfig, "app")
    @patch("apps.slack.services.message_auto_reply.Message.objects.get")
    @patch("apps.slack.services.message_auto_reply.process_ai_query")
    @patch("apps.slack.services.message_auto_reply.markdown_blocks")
    def test_generate_ai_reply_success(
        self,
        mock_markdown_blocks,
        mock_process_ai_query,
        mock_message_get,
        mock_app,
        mock_message,
    ):
        """Test successful AI reply generation."""
        mock_message_get.return_value = mock_message
        ai_text = "OWASP is a security organization..."
        mock_process_ai_query.return_value = ai_text
        response_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ai_text,
                },
            }
        ]
        mock_markdown_blocks.return_value = response_blocks
        mock_client = Mock()
        mock_app.client = mock_client
        mock_client.conversations_replies.return_value = {"messages": [{"reply_count": 0}]}

        generate_ai_reply_if_unanswered(mock_message.id)

        mock_client.conversations_replies.assert_called_once_with(
            channel=mock_message.conversation.slack_channel_id,
            ts=mock_message.slack_message_id,
            limit=1,
        )
        mock_process_ai_query.assert_called_once_with(
            query=mock_message.text, channel_id=mock_message.conversation.slack_channel_id
        )
        mock_markdown_blocks.assert_called_once_with(format_ai_response_for_slack(ai_text))
        block_posts = [
            c
            for c in mock_client.chat_postMessage.call_args_list
            if c.kwargs.get("blocks") is not None
        ]
        assert len(block_posts) == 1
        assert block_posts[0].kwargs["blocks"] == response_blocks
        formatted = format_ai_response_for_slack(ai_text)
        assert block_posts[0].kwargs["text"] == truncate_for_slack_fallback(formatted)
        assert block_posts[0].kwargs["thread_ts"] == mock_message.slack_message_id

    @patch("apps.slack.services.message_auto_reply.Message.objects.get")
    def test_generate_ai_reply_message_not_found(self, mock_message_get):
        """Test handling when message doesn't exist."""
        mock_message_get.side_effect = Message.DoesNotExist()

        generate_ai_reply_if_unanswered(99999)

    @patch.object(SlackConfig, "app", None)
    @patch("apps.slack.services.message_auto_reply.Message.objects.get")
    @patch("apps.slack.services.message_auto_reply.logger")
    def test_generate_ai_reply_slack_app_not_configured(
        self, mock_logger, mock_message_get, mock_message
    ):
        """Test when Slack app is not configured."""
        mock_message_get.return_value = mock_message

        generate_ai_reply_if_unanswered(mock_message.id)

        mock_logger.warning.assert_called_once_with("Slack app is not configured")

    @patch("apps.slack.services.message_auto_reply.Message.objects.get")
    @patch("apps.slack.services.message_auto_reply.process_ai_query")
    def test_generate_ai_reply_assistant_disabled(
        self, mock_process_ai_query, mock_message_get, mock_message
    ):
        """Test when assistant is disabled for conversation."""
        mock_message.conversation.is_nest_bot_assistant_enabled = False
        mock_message_get.return_value = mock_message

        generate_ai_reply_if_unanswered(mock_message.id)

        mock_process_ai_query.assert_not_called()

    @patch.object(SlackConfig, "app")
    @patch("apps.slack.services.message_auto_reply.Message.objects.get")
    @patch("apps.slack.services.message_auto_reply.process_ai_query")
    def test_generate_ai_reply_has_thread_replies(
        self, mock_process_ai_query, mock_message_get, mock_app, mock_message
    ):
        """Test when message already has replies."""
        mock_message_get.return_value = mock_message
        mock_client = Mock()
        mock_app.client = mock_client
        mock_client.conversations_replies.return_value = {"messages": [{"reply_count": 2}]}

        generate_ai_reply_if_unanswered(mock_message.id)

        mock_process_ai_query.assert_not_called()

    @patch.object(SlackConfig, "app")
    @patch("apps.slack.services.message_auto_reply.Message.objects.get")
    @patch("apps.slack.services.message_auto_reply.process_ai_query")
    @patch("apps.slack.services.message_auto_reply.markdown_blocks")
    @patch("apps.slack.services.message_auto_reply.logger")
    def test_generate_ai_reply_slack_api_error(
        self,
        mock_logger,
        mock_markdown_blocks,
        mock_process_ai_query,
        mock_message_get,
        mock_app,
        mock_message,
    ):
        """Test when Slack API error occurs while checking replies."""
        mock_message_get.return_value = mock_message
        mock_client = Mock()
        mock_app.client = mock_client
        mock_client.conversations_replies.side_effect = SlackApiError("API Error", response=Mock())
        ai_text = "OWASP is a security organization..."
        mock_process_ai_query.return_value = ai_text
        mock_markdown_blocks.return_value = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ai_text,
                },
            }
        ]

        generate_ai_reply_if_unanswered(mock_message.id)

        mock_logger.exception.assert_called_once_with("Error checking for replies for message")
        mock_process_ai_query.assert_called_once()
        assert mock_client.chat_postMessage.call_count >= 1

    @patch.object(SlackConfig, "app")
    @patch("apps.slack.services.message_auto_reply.Message.objects.get")
    @patch("apps.slack.services.message_auto_reply.process_ai_query")
    def test_generate_ai_reply_no_ai_response(
        self,
        mock_process_ai_query,
        mock_message_get,
        mock_app,
        mock_message,
    ):
        """Test when AI doesn't return a response."""
        mock_message_get.return_value = mock_message
        mock_client = Mock()
        mock_app.client = mock_client
        mock_client.conversations_replies.return_value = {"messages": [{"reply_count": 0}]}
        mock_process_ai_query.return_value = None

        generate_ai_reply_if_unanswered(mock_message.id)

        post_texts = [c.kwargs.get("text") for c in mock_client.chat_postMessage.call_args_list]
        assert ERROR_UNABLE_TO_GENERATE_RESPONSE in post_texts

    @patch.object(SlackConfig, "app")
    @patch("apps.slack.services.message_auto_reply.Message.objects.get")
    @patch("apps.slack.services.message_auto_reply.process_ai_query")
    def test_generate_ai_reply_empty_response(
        self,
        mock_process_ai_query,
        mock_message_get,
        mock_app,
        mock_message,
    ):
        """Test when AI returns empty response."""
        mock_message_get.return_value = mock_message
        mock_client = Mock()
        mock_app.client = mock_client
        mock_client.conversations_replies.return_value = {"messages": [{"reply_count": 0}]}
        mock_process_ai_query.return_value = ""

        generate_ai_reply_if_unanswered(mock_message.id)

        post_texts = [c.kwargs.get("text") for c in mock_client.chat_postMessage.call_args_list]
        assert ERROR_UNABLE_TO_GENERATE_RESPONSE in post_texts

    @patch.object(SlackConfig, "app")
    @patch("apps.slack.services.message_auto_reply.Message.objects.get")
    @patch("apps.slack.services.message_auto_reply.process_ai_query")
    def test_generate_ai_reply_empty_after_formatting(
        self,
        mock_process_ai_query,
        mock_message_get,
        mock_app,
        mock_message,
    ):
        """Whitespace-only after formatting is treated as no answer."""
        mock_message_get.return_value = mock_message
        mock_client = Mock()
        mock_app.client = mock_client
        mock_client.conversations_replies.return_value = {"messages": [{"reply_count": 0}]}
        mock_process_ai_query.return_value = "```\n```"

        generate_ai_reply_if_unanswered(mock_message.id)

        post_texts = [c.kwargs.get("text") for c in mock_client.chat_postMessage.call_args_list]
        assert ERROR_UNABLE_TO_GENERATE_RESPONSE in post_texts
        block_posts = [
            c for c in mock_client.chat_postMessage.call_args_list if c.kwargs.get("blocks")
        ]
        assert not block_posts

    @patch("apps.ai.flows.process_query")
    @patch.object(SlackConfig, "app")
    @patch("apps.slack.services.message_auto_reply.Message.objects.get")
    def test_generate_ai_reply_bare_yes_from_pipeline(
        self,
        mock_message_get,
        mock_app,
        mock_process_query,
        mock_message,
    ):
        """Bare YES from the pipeline yields no block reply."""
        mock_message_get.return_value = mock_message
        mock_client = Mock()
        mock_app.client = mock_client
        mock_client.conversations_replies.return_value = {"messages": [{"reply_count": 0}]}
        mock_process_query.return_value = "YES"

        generate_ai_reply_if_unanswered(mock_message.id)

        post_texts = [c.kwargs.get("text") for c in mock_client.chat_postMessage.call_args_list]
        assert ERROR_UNABLE_TO_GENERATE_RESPONSE in post_texts
        block_posts = [
            c for c in mock_client.chat_postMessage.call_args_list if c.kwargs.get("blocks")
        ]
        assert not block_posts
