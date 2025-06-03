"""Tests for the slack_sync_messages management command."""

from io import StringIO
from unittest.mock import MagicMock, Mock, patch

import pytest
from django.core.management import call_command

from apps.slack.management.commands.slack_sync_messages import Command
from apps.slack.models import Conversation, Member, Message, Workspace

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
        conversation.workspace = Mock()
        return conversation

    @pytest.fixture
    def mock_member(self):
        """Create a mock member."""
        member = Mock(spec=Member)
        member.slack_user_id = "U12345"
        return member

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
            command.handle(batch_size=200, delay=0.5, channel_id=None)

        output = stdout.getvalue()
        assert "No workspaces found in the database" in output

    def test_handle_workspace_no_token(self, command, mock_workspace_no_token, mock_conversation):
        """Test handle when workspace has no bot token."""
        mock_workspaces = Mock()
        mock_workspaces.exists.return_value = True
        mock_workspaces.__iter__ = Mock(return_value=iter([mock_workspace_no_token]))

        stdout = StringIO()
        with patch.object(Workspace.objects, "all", return_value=mock_workspaces):
            command.stdout = stdout
            command.handle(batch_size=200, delay=0.5, channel_id=None)

        output = stdout.getvalue()
        assert "No bot token found for Workspace No Token" in output

    @patch("apps.slack.management.commands.slack_sync_messages.WebClient")
    @patch("apps.slack.management.commands.slack_sync_messages.time.sleep")
    def test_handle_successful_sync(
        self,
        mock_sleep,
        mock_web_client,
        command,
        mock_workspace,
        mock_conversation,
        mock_member,
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

        mock_message = Mock(spec=Message)
        mock_message.is_thread_parent = True
        mock_message.slack_message_id = TEST_THREAD_TS

        stdout = StringIO()
        with (
            patch.object(Workspace.objects, "all", return_value=mock_workspaces),
            patch.object(Conversation.objects, "filter", return_value=mock_conversations),
            patch.object(Message.objects, "filter") as mock_message_filter,
            patch.object(Member.objects, "get", return_value=mock_member),
            patch.object(Message, "update_data", return_value=mock_message),
            patch.object(Message, "bulk_save") as mock_bulk_save,
        ):
            mock_message_filter.return_value.order_by.return_value.first.return_value = None
            command.stdout = stdout
            command.handle(batch_size=200, delay=0.5, channel_id=None)

        assert mock_client.conversations_history.call_count == CONSTANT_2
        mock_bulk_save.assert_called()

        output = stdout.getvalue()
        assert "Processing workspace: Test Workspace" in output
        assert "Processing channel: general" in output
        assert "Finished processing all workspaces" in output

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
            is_thread_reply=False,
            parent_message=None,
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
            is_thread_reply=False,
            parent_message=None,
        )

        assert result is None

    def test_create_message_from_data_no_user(self, command, mock_conversation):
        """Test _create_message_from_data with no user or bot_id."""
        message_data = {
            "ts": TEST_MESSAGE_TS,
            "text": "Hello world!",
        }

        result = command._create_message_from_data(
            client=Mock(),
            message_data=message_data,
            conversation=mock_conversation,
            is_thread_reply=False,
            parent_message=None,
        )

        assert result is None

    def test_create_message_from_data_member_not_found(self, command, mock_conversation):
        """Test _create_message_from_data when member is not found."""
        message_data = {
            "ts": TEST_MESSAGE_TS,
            "text": "Hello world!",
            "user": "U12345",
        }

        stdout = StringIO()
        with patch.object(Member.objects, "get", side_effect=Member.DoesNotExist):
            command.stdout = stdout
            result = command._create_message_from_data(
                client=Mock(),
                message_data=message_data,
                conversation=mock_conversation,
                is_thread_reply=False,
                parent_message=None,
            )

        assert result is None
        output = stdout.getvalue()
        assert "Member U12345 not found in database" in output

    @patch("apps.slack.management.commands.slack_sync_messages.Message.update_data")
    def test_create_message_from_data_regular_message(
        self, mock_update_data, command, mock_conversation, mock_member
    ):
        """Test _create_message_from_data with regular message."""
        message_data = {
            "ts": TEST_MESSAGE_TS,
            "text": "Hello world!",
            "user": "U12345",
        }

        mock_message = Mock(spec=Message)
        mock_update_data.return_value = mock_message

        with patch.object(Member.objects, "get", return_value=mock_member):
            result = command._create_message_from_data(
                client=Mock(),
                message_data=message_data,
                conversation=mock_conversation,
                is_thread_reply=False,
                parent_message=None,
            )

        assert result is mock_message
        mock_update_data.assert_called_once_with(
            data=message_data,
            conversation=mock_conversation,
            author=mock_member,
            is_thread_reply=False,
            parent_message=None,
            save=False,
        )

    def test_fetch_thread_replies_no_parents(self, command, mock_conversation):
        """Test _fetch_thread_replies with no parent messages."""
        mock_client = Mock()

        stdout = StringIO()
        command.stdout = stdout

        command._fetch_thread_replies(
            client=mock_client,
            conversation=mock_conversation,
            parent_messages=[],
            delay=0.5,
        )

        output = stdout.getvalue()
        assert "No threaded parent messages to process" in output

    @patch("apps.slack.management.commands.slack_sync_messages.time.sleep")
    def test_fetch_thread_replies_success(
        self, mock_sleep, command, mock_conversation, mock_member, mock_slack_replies_response
    ):
        """Test _fetch_thread_replies successful execution."""
        mock_client = Mock()
        mock_client.conversations_replies.return_value = mock_slack_replies_response

        mock_parent = Mock(spec=Message)
        mock_parent.slack_message_id = TEST_THREAD_TS

        mock_reply = Mock(spec=Message)

        stdout = StringIO()
        command.stdout = stdout

        with (
            patch.object(Message.objects, "filter") as mock_filter,
            patch.object(Member.objects, "get", return_value=mock_member),
            patch.object(Message, "update_data", return_value=mock_reply),
            patch.object(Message, "bulk_save") as mock_bulk_save,
        ):
            mock_filter.return_value.order_by.return_value.first.return_value = None

            command._fetch_thread_replies(
                client=mock_client,
                conversation=mock_conversation,
                parent_messages=[mock_parent],
                delay=0.5,
            )

        mock_client.conversations_replies.assert_called_once()
        mock_bulk_save.assert_called_once()

    def test_handle_slack_response_with_invalid_response(self, command):
        """Test _handle_slack_response with invalid response."""
        stdout = StringIO()
        command.stdout = stdout

        response = {"ok": False}
        command._handle_slack_response(response, "conversations_history")

        output = stdout.getvalue()
        assert "conversations_history API call failed" in output

    def test_handle_slack_response_with_valid_response(self, command):
        """Test _handle_slack_response with valid response."""
        response = {"ok": True, "messages": []}
        command._handle_slack_response(response, "conversations_history")

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

        with patch.object(Workspace.objects, "all") as mock_all:
            mock_all.return_value.exists.return_value = False
            call_command("slack_sync_messages", stdout=stdout)

        output = stdout.getvalue()
        assert "No workspaces found in the database" in output
