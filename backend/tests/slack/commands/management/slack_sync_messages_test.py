"""Tests for the slack_sync_messages management command."""

from datetime import UTC, datetime
from io import StringIO
from unittest.mock import MagicMock, Mock, patch

import pytest
from django.core.management import call_command
from slack_sdk.errors import SlackApiError

from apps.slack.management.commands.slack_sync_messages import Command
from apps.slack.models import Conversation, Message, Workspace

CONSTANT_2 = 2
CONSTANT_3 = 3
CONSTANT_4 = 4
TEST_TOKEN = "xoxb-test-token"  # noqa: S105
TEST_TOKEN_1 = "xoxb-token-1"  # noqa: S105
TEST_TOKEN_2 = "xoxb-token-2"  # noqa: S105
TEST_CHANNEL_ID = "C12345"
TEST_MESSAGE_TS = "1605000000.000100"
TEST_THREAD_TS = "1605000000.000200"


class TestSlackSyncMessagesCommand:
    """Test cases for the slack_sync_messages management command."""

    @pytest.fixture
    def command(self):
        """Create a Command instance for testing."""
        return Command()

    @pytest.fixture
    def mock_workspace(self):
        """Create a mock workspace."""
        workspace = Mock(spec=Workspace)
        workspace.name = "Test Workspace"
        workspace.__str__ = Mock(return_value="Test Workspace")
        workspace.bot_token = TEST_TOKEN
        return workspace

    @pytest.fixture
    def mock_workspace_no_token(self):
        """Create a mock workspace without a bot token."""
        workspace = Mock(spec=Workspace)
        workspace.name = "Workspace No Token"
        workspace.__str__ = Mock(return_value="Workspace No Token")
        workspace.bot_token = None
        return workspace

    @pytest.fixture
    def mock_conversation(self):
        """Create a mock conversation."""
        conversation = Mock(spec=Conversation)
        conversation.name = "general"
        conversation.slack_channel_id = TEST_CHANNEL_ID
        return conversation

    @pytest.fixture
    def mock_slack_history_response(self):
        """Create a mock Slack conversations_history response."""
        return {
            "ok": True,
            "messages": [
                {
                    "ts": TEST_MESSAGE_TS,
                    "text": "Hello world!",
                    "user": "U12345",
                    "type": "message",
                },
                {
                    "ts": TEST_THREAD_TS,
                    "text": "This is a thread parent",
                    "user": "U67890",
                    "type": "message",
                    "reply_count": 2,
                    "thread_ts": TEST_THREAD_TS,
                },
                {
                    "ts": "1605000000.000300",
                    "text": "Thread reply",
                    "user": "U11111",
                    "type": "message",
                    "thread_ts": TEST_THREAD_TS,
                },
            ],
            "response_metadata": {
                "next_cursor": "next-cursor-123",
            },
        }

    @pytest.fixture
    def mock_slack_history_response_final(self):
        """Create a mock Slack conversations_history response with no next cursor."""
        return {
            "ok": True,
            "messages": [
                {
                    "ts": "1605000000.000400",
                    "text": "Final message",
                    "user": "U22222",
                    "type": "message",
                },
            ],
            "response_metadata": {},
        }

    @pytest.fixture
    def mock_slack_replies_response(self):
        """Create a mock Slack conversations_replies response."""
        return {
            "ok": True,
            "messages": [
                {
                    "ts": TEST_THREAD_TS,
                    "text": "This is a thread parent",
                    "user": "U67890",
                    "type": "message",
                    "reply_count": 2,
                    "thread_ts": TEST_THREAD_TS,
                },
                {
                    "ts": "1605000000.000301",
                    "text": "First reply",
                    "user": "U11111",
                    "type": "message",
                    "thread_ts": TEST_THREAD_TS,
                },
                {
                    "ts": "1605000000.000302",
                    "text": "Second reply",
                    "user": "U33333",
                    "type": "message",
                    "thread_ts": TEST_THREAD_TS,
                },
            ],
        }

    def test_handle_no_workspaces(self, command):
        """Test handle when no workspaces exist."""
        stdout = StringIO()
        with patch.object(Workspace.objects, "all") as mock_all:
            mock_all.return_value.exists.return_value = False
            command.stdout = stdout
            command.handle(batch_size=200, delay=0.5, channel_id=None, include_threads=True)

        output = stdout.getvalue()
        assert "No workspaces found in the database" in output

    @patch("apps.slack.management.commands.slack_sync_messages.WebClient")
    @patch("apps.slack.management.commands.slack_sync_messages.time.sleep")
    def test_handle_successful_sync(
        self,
        mock_sleep,
        mock_web_client,
        command,
        mock_workspace,
        mock_conversation,
        mock_slack_history_response,
        mock_slack_history_response_final,
        mock_slack_replies_response,
    ):
        """Test successful synchronization of messages."""
        mock_workspaces = Mock()
        mock_workspaces.exists.return_value = True
        mock_workspaces.__iter__ = Mock(return_value=iter([mock_workspace]))

        mock_conversations = Mock()
        mock_conversations.__iter__ = Mock(return_value=iter([mock_conversation]))

        mock_client = Mock()
        mock_web_client.return_value = mock_client

        mock_client.conversations_history.side_effect = [
            mock_slack_history_response,
            mock_slack_history_response_final,
        ]

        mock_client.conversations_replies.return_value = mock_slack_replies_response

        mock_last_message = Mock()
        mock_last_message.timestamp = datetime.fromtimestamp(1605000000, tz=UTC)

        stdout = StringIO()
        with (
            patch.object(Workspace.objects, "all", return_value=mock_workspaces),
            patch.object(Conversation.objects, "filter", return_value=mock_conversations),
            patch.object(Message.objects, "filter") as mock_message_filter,
            patch.object(Message, "update_data") as mock_update_data,
            patch.object(Message, "bulk_save") as mock_bulk_save,
            patch("builtins.print"),
        ):
            mock_message_filter.return_value.order_by.return_value.first.return_value = (
                mock_last_message
            )
            mock_message_instance = Mock(spec=Message)
            mock_update_data.return_value = mock_message_instance
            command.stdout = stdout
            command.handle(batch_size=200, delay=0.5, channel_id=None, include_threads=True)

        assert mock_client.conversations_history.call_count == CONSTANT_2
        mock_client.conversations_replies.assert_called_once_with(
            channel=TEST_CHANNEL_ID, ts=TEST_THREAD_TS
        )

        mock_bulk_save.assert_called()

        output = stdout.getvalue()
        assert "Processing workspace: Test Workspace" in output
        assert "Processing channel: general" in output
        assert "Finished processing all workspaces" in output

    @patch("apps.slack.management.commands.slack_sync_messages.WebClient")
    def test_handle_api_error(
        self,
        mock_web_client,
        command,
        mock_workspace,
        mock_conversation,
    ):
        """Test handling SlackApiError during conversations_history."""
        mock_workspaces = Mock()
        mock_workspaces.exists.return_value = True
        mock_workspaces.__iter__ = Mock(return_value=iter([mock_workspace]))

        mock_conversations = Mock()
        mock_conversations.__iter__ = Mock(return_value=iter([mock_conversation]))

        mock_client = Mock()
        mock_web_client.return_value = mock_client

        error_response = {"error": "channel_not_found"}
        mock_client.conversations_history.side_effect = SlackApiError(
            "Error", response=error_response
        )

        stdout = StringIO()
        with (
            patch.object(Workspace.objects, "all", return_value=mock_workspaces),
            patch.object(Conversation.objects, "filter", return_value=mock_conversations),
            patch.object(Message.objects, "filter") as mock_message_filter,
        ):
            mock_message_filter.return_value.order_by.return_value.first.return_value = None
            command.stdout = stdout
            command.handle(batch_size=200, delay=0.5, channel_id=None, include_threads=True)

        output = stdout.getvalue()
        assert "Failed to fetch messages for general: channel_not_found" in output

    @patch("apps.slack.management.commands.slack_sync_messages.WebClient")
    def test_handle_no_messages_returned(
        self,
        mock_web_client,
        command,
        mock_workspace,
        mock_conversation,
    ):
        """Test handling when no messages are returned."""
        mock_workspaces = Mock()
        mock_workspaces.exists.return_value = True
        mock_workspaces.__iter__ = Mock(return_value=iter([mock_workspace]))

        mock_conversations = Mock()
        mock_conversations.__iter__ = Mock(return_value=iter([mock_conversation]))

        mock_client = Mock()
        mock_web_client.return_value = mock_client

        empty_response = {
            "ok": True,
            "messages": [],
            "response_metadata": {},
        }
        mock_client.conversations_history.return_value = empty_response

        stdout = StringIO()
        with (
            patch.object(Workspace.objects, "all", return_value=mock_workspaces),
            patch.object(Conversation.objects, "filter", return_value=mock_conversations),
            patch.object(Message.objects, "filter") as mock_message_filter,
            patch.object(Message, "bulk_save") as mock_bulk_save,
        ):
            mock_message_filter.return_value.order_by.return_value.first.return_value = None
            command.stdout = stdout
            command.handle(batch_size=200, delay=0.5, channel_id=None, include_threads=True)

        mock_bulk_save.assert_not_called()

    def test_create_message_from_data_channel_join_subtype(self, command, mock_conversation):
        """Test _create_message_from_data with channel_join subtype."""
        message_data = {
            "ts": TEST_MESSAGE_TS,
            "subtype": "channel_join",
            "text": "User joined channel",
        }

        result = command._create_message_from_data(
            client=Mock(),
            message_data=message_data,
            conversation=mock_conversation,
            include_threads=True,
        )

        assert result is None

    def test_create_message_from_data_no_content(self, command, mock_conversation):
        """Test _create_message_from_data with no text, attachments, or files."""
        message_data = {
            "ts": TEST_MESSAGE_TS,
            "user": "U12345",
        }

        result = command._create_message_from_data(
            client=Mock(),
            message_data=message_data,
            conversation=mock_conversation,
            include_threads=True,
        )

        assert result is None

    def test_create_message_from_data_thread_reply_excluded(self, command, mock_conversation):
        """Test _create_message_from_data excludes thread replies when include_threads=True."""
        message_data = {
            "ts": "1605000000.000300",
            "text": "This is a reply",
            "user": "U12345",
            "thread_ts": TEST_THREAD_TS,
        }

        result = command._create_message_from_data(
            client=Mock(),
            message_data=message_data,
            conversation=mock_conversation,
            include_threads=True,
        )

        assert result is None

    @patch("apps.slack.management.commands.slack_sync_messages.Message.update_data")
    def test_create_message_from_data_regular_message(
        self, mock_update_data, command, mock_conversation
    ):
        """Test _create_message_from_data with regular message."""
        message_data = {
            "ts": TEST_MESSAGE_TS,
            "text": "Hello world!",
            "user": "U12345",
        }

        mock_message = Mock(spec=Message)
        mock_update_data.return_value = mock_message

        with patch("builtins.print"):
            result = command._create_message_from_data(
                client=Mock(),
                message_data=message_data,
                conversation=mock_conversation,
                include_threads=True,
            )

        assert result is mock_message
        mock_update_data.assert_called_once_with(
            {
                "slack_message_id": TEST_MESSAGE_TS,
                "conversation": mock_conversation,
                "text": "Hello world!",
                "timestamp": TEST_MESSAGE_TS,
                "is_thread": False,
            },
            save=False,
        )

    @patch("apps.slack.management.commands.slack_sync_messages.Message.update_data")
    def test_create_message_from_data_thread_parent_with_replies(
        self, mock_update_data, command, mock_conversation, mock_slack_replies_response
    ):
        """Test _create_message_from_data with thread parent and replies."""
        message_data = {
            "ts": TEST_THREAD_TS,
            "text": "This is a thread parent",
            "user": "U67890",
            "reply_count": 2,
            "thread_ts": TEST_THREAD_TS,
        }

        mock_client = Mock()
        mock_client.conversations_replies.return_value = mock_slack_replies_response

        mock_message = Mock(spec=Message)
        mock_update_data.return_value = mock_message

        stdout = StringIO()
        with patch("builtins.print"):
            command.stdout = stdout
            result = command._create_message_from_data(
                client=mock_client,
                message_data=message_data,
                conversation=mock_conversation,
                include_threads=True,
            )

        assert result is mock_message

        mock_client.conversations_replies.assert_called_once_with(
            channel=TEST_CHANNEL_ID, ts=TEST_THREAD_TS
        )

        expected_combined_text = "This is a thread parent\n\nFirst reply\n\nSecond reply"
        mock_update_data.assert_called_once_with(
            {
                "slack_message_id": TEST_THREAD_TS,
                "conversation": mock_conversation,
                "text": expected_combined_text,
                "timestamp": TEST_THREAD_TS,
                "is_thread": True,
            },
            save=False,
        )

    @patch("apps.slack.management.commands.slack_sync_messages.Message.update_data")
    def test_create_message_from_data_thread_replies_api_error(
        self, mock_update_data, command, mock_conversation
    ):
        """Test _create_message_from_data when conversations_replies fails."""
        message_data = {
            "ts": TEST_THREAD_TS,
            "text": "This is a thread parent",
            "user": "U67890",
            "reply_count": 2,
            "thread_ts": TEST_THREAD_TS,
        }

        mock_client = Mock()
        mock_client.conversations_replies.side_effect = SlackApiError(
            "Error", response={"error": "thread_not_found"}
        )

        mock_message = Mock(spec=Message)
        mock_update_data.return_value = mock_message

        stdout = StringIO()
        with patch("builtins.print"):
            command.stdout = stdout
            result = command._create_message_from_data(
                client=mock_client,
                message_data=message_data,
                conversation=mock_conversation,
                include_threads=True,
            )

        assert result is mock_message

        mock_update_data.assert_called_once_with(
            {
                "slack_message_id": TEST_THREAD_TS,
                "conversation": mock_conversation,
                "text": "This is a thread parent",
                "timestamp": TEST_THREAD_TS,
                "is_thread": True,
            },
            save=False,
        )

    def test_handle_slack_response_with_invalid_response(self, command):
        """Test _handle_slack_response with invalid response."""
        stdout = StringIO()
        command.stdout = stdout

        response = {"ok": False}
        result = command._handle_slack_response(response, "conversations_history")

        assert result is None
        output = stdout.getvalue()
        assert "conversations_history API call failed" in output

    def test_handle_slack_response_with_valid_response(self, command):
        """Test _handle_slack_response with valid response."""
        response = {"ok": True, "messages": []}
        result = command._handle_slack_response(response, "conversations_history")

        assert result is None

    def test_add_arguments(self, command):
        """Test add_arguments method."""
        parser = MagicMock()
        command.add_arguments(parser)

        assert parser.add_argument.call_count == CONSTANT_3

        parser.add_argument.assert_any_call(
            "--batch-size",
            type=int,
            default=200,
            help="Number of messages to retrieve per request",
        )

        parser.add_argument.assert_any_call(
            "--delay",
            type=float,
            default=0.5,
            help="Delay between API requests in seconds",
        )

        parser.add_argument.assert_any_call(
            "--channel-id",
            type=str,
            help="Specific channel ID to fetch messages from",
        )

    def test_management_command_via_call_command(self):
        """Test running the command via Django's call_command."""
        stdout = StringIO()

        with (
            patch.object(Workspace.objects, "all") as mock_all,
            patch("builtins.print") as mock_print,
        ):
            mock_all.return_value.exists.return_value = False
            call_command("slack_sync_messages", stdout=stdout)

        output = stdout.getvalue()
        assert "No workspaces found in the database" in output
        mock_print.assert_not_called()
