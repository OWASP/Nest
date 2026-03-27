"""Tests for the slack_sync_data management command."""

from io import StringIO
from unittest.mock import MagicMock, Mock, patch

import pytest
from django.core.management import call_command
from slack_sdk.errors import SlackApiError

from apps.slack.management.commands.slack_sync_data import Command
from apps.slack.models import Conversation, Member, Workspace

CONSTANT_2 = 2
CONSTANT_3 = 3
TEST_TOKEN = "xoxb-test-token"  # noqa: S105
TEST_TOKEN_1 = "xoxb-token-1"  # noqa: S105
TEST_TOKEN_2 = "xoxb-token-2"  # noqa: S105


class TestSlackSyncDataCommand:
    """Test cases for the slack_sync_data management command."""

    @pytest.fixture
    def command(self):
        """Create a Command instance for testing."""
        return Command()

    @pytest.fixture
    def mock_workspace(self):
        """Create a mock workspace."""
        workspace = Mock(spec=Workspace)
        workspace.__str__ = Mock(return_value="Test Workspace")
        workspace.bot_token = TEST_TOKEN
        return workspace

    @pytest.fixture
    def mock_workspace_no_token(self):
        """Create a mock workspace without a bot token."""
        workspace = Mock(spec=Workspace)
        workspace.__str__ = Mock(return_value="Workspace No Token")
        workspace.bot_token = None
        return workspace

    @pytest.fixture
    def mock_slack_conversations_response(self):
        """Create a mock Slack conversations_list response."""
        return {
            "ok": True,
            "channels": [
                {
                    "id": "C12345",
                    "name": "general",
                    "created": "1605000000",
                    "is_private": False,
                    "is_archived": False,
                    "is_general": True,
                    "topic": {"value": "General discussion"},
                    "purpose": {"value": "General purpose"},
                    "creator": "U12345",
                },
                {
                    "id": "C67890",
                    "name": "random",
                    "created": "1605000001",
                    "is_private": True,
                    "is_archived": False,
                    "is_general": False,
                    "topic": {"value": "Random chat"},
                    "purpose": {"value": "Random discussions"},
                    "creator": "U67890",
                },
            ],
            "response_metadata": {
                "next_cursor": "next-cursor-123",
            },
        }

    @pytest.fixture
    def mock_slack_conversations_response_final(self):
        """Create a mock Slack conversations_list response with no next cursor."""
        return {
            "ok": True,
            "channels": [
                {
                    "id": "C11111",
                    "name": "dev",
                    "created": "1605000002",
                    "is_private": False,
                    "is_archived": True,
                    "is_general": False,
                    "topic": {"value": "Development"},
                    "purpose": {"value": "Development discussions"},
                    "creator": "U11111",
                },
            ],
            "response_metadata": {},
        }

    @pytest.fixture
    def mock_slack_users_response(self):
        """Create a mock Slack users_list response."""
        return {
            "ok": True,
            "members": [
                {
                    "id": "U12345",
                    "name": "john.doe",
                    "real_name": "John Doe",
                    "is_bot": False,
                    "profile": {
                        "email": "john.doe@example.com",
                    },
                },
                {
                    "id": "U67890",
                    "name": "jane.smith",
                    "real_name": "Jane Smith",
                    "is_bot": False,
                    "profile": {
                        "email": "jane.smith@example.com",
                    },
                },
            ],
            "response_metadata": {
                "next_cursor": "user-cursor-123",
            },
        }

    @pytest.fixture
    def mock_slack_users_response_final(self):
        """Create a mock Slack users_list response with no next cursor."""
        return {
            "ok": True,
            "members": [
                {
                    "id": "BOT123",
                    "name": "test.bot",
                    "real_name": "Test Bot",
                    "is_bot": True,
                    "profile": {
                        "email": "",
                    },
                },
            ],
            "response_metadata": {},
        }

    def test_handle_no_workspaces(self, command):
        """Test handle when no workspaces exist."""
        stdout = StringIO()
        with patch.object(Workspace.objects, "all") as mock_all:
            mock_all.return_value.exists.return_value = False
            command.stdout = stdout
            command.handle(batch_size=1000, delay=0.5)

        output = stdout.getvalue()
        assert "No workspaces found in the database" in output

    @patch("apps.slack.management.commands.slack_sync_data.WebClient")
    @patch("apps.slack.management.commands.slack_sync_data.time.sleep")
    def test_handle_successful_sync(
        self,
        mock_sleep,
        mock_web_client,
        command,
        mock_workspace,
        mock_slack_conversations_response,
        mock_slack_conversations_response_final,
        mock_slack_users_response,
        mock_slack_users_response_final,
    ):
        """Test successful synchronization of conversations and members."""
        mock_workspaces = Mock()
        mock_workspaces.exists.return_value = True
        mock_workspaces.__iter__ = Mock(return_value=iter([mock_workspace]))

        mock_client = Mock()
        mock_web_client.return_value = mock_client

        mock_client.conversations_list.side_effect = [
            mock_slack_conversations_response,
            mock_slack_conversations_response_final,
        ]
        mock_client.users_list.side_effect = [
            mock_slack_users_response,
            mock_slack_users_response_final,
        ]

        mock_conversation1 = Mock()
        mock_conversation2 = Mock()
        mock_conversation3 = Mock()

        mock_member1 = Mock()
        mock_member2 = Mock()
        mock_member3 = Mock()

        stdout = StringIO()
        with (
            patch.object(Workspace.objects, "all", return_value=mock_workspaces),
            patch.object(Conversation, "update_data") as mock_conv_update,
            patch.object(Conversation, "bulk_save") as mock_conv_bulk_save,
            patch.object(Member, "update_data") as mock_member_update,
            patch.object(Member, "bulk_save") as mock_member_bulk_save,
        ):
            mock_conv_update.side_effect = [
                mock_conversation1,
                mock_conversation2,
                mock_conversation3,
            ]
            mock_member_update.side_effect = [mock_member1, mock_member2, mock_member3]

            command.stdout = stdout
            command.handle(batch_size=10, delay=0.1)

        mock_web_client.assert_called_once_with(token=TEST_TOKEN)

        assert mock_client.conversations_list.call_count == CONSTANT_2
        mock_client.conversations_list.assert_any_call(
            cursor=None,
            exclude_archived=False,
            limit=10,
            timeout=30,
            types="public_channel,private_channel",
        )
        mock_client.conversations_list.assert_any_call(
            cursor="next-cursor-123",
            exclude_archived=False,
            limit=10,
            timeout=30,
            types="public_channel,private_channel",
        )

        assert mock_client.users_list.call_count == CONSTANT_2
        mock_client.users_list.assert_any_call(cursor=None, limit=10, timeout=30)
        mock_client.users_list.assert_any_call(cursor="user-cursor-123", limit=10, timeout=30)

        assert mock_conv_update.call_count == CONSTANT_3
        mock_conv_update.assert_any_call(
            mock_slack_conversations_response["channels"][0], mock_workspace
        )
        mock_conv_update.assert_any_call(
            mock_slack_conversations_response["channels"][1], mock_workspace
        )
        mock_conv_update.assert_any_call(
            mock_slack_conversations_response_final["channels"][0], mock_workspace
        )

        assert mock_member_update.call_count == CONSTANT_3
        mock_member_update.assert_any_call(mock_slack_users_response["members"][0], mock_workspace)
        mock_member_update.assert_any_call(mock_slack_users_response["members"][1], mock_workspace)
        mock_member_update.assert_any_call(
            mock_slack_users_response_final["members"][0], mock_workspace
        )

        mock_conv_bulk_save.assert_called_once_with(
            [
                mock_conversation1,
                mock_conversation2,
                mock_conversation3,
            ]
        )
        mock_member_bulk_save.assert_called_once_with([mock_member1, mock_member2, mock_member3])

        mock_sleep.assert_called_with(0.1)

        output = stdout.getvalue()
        assert "Processing workspace: Test Workspace" in output
        assert "Fetching conversations for Test Workspace" in output
        assert "Populated 3 channels" in output
        assert "Fetching members for Test Workspace" in output
        assert "Populated 3 members" in output
        assert "Finished processing all workspaces" in output

    @patch("apps.slack.management.commands.slack_sync_data.WebClient")
    def test_handle_workspace_without_bot_token(
        self, mock_web_client, command, mock_workspace_no_token
    ):
        """Test handling workspace without bot token."""
        mock_workspaces = Mock()
        mock_workspaces.exists.return_value = True
        mock_workspaces.__iter__ = Mock(return_value=iter([mock_workspace_no_token]))

        stdout = StringIO()
        with patch.object(Workspace.objects, "all", return_value=mock_workspaces):
            command.stdout = stdout
            command.handle(batch_size=1000, delay=0.5)

        mock_web_client.assert_not_called()

        output = stdout.getvalue()
        assert "Processing workspace: Workspace No Token" in output
        assert "No bot token found for Workspace No Token" in output

    @patch("apps.slack.management.commands.slack_sync_data.WebClient")
    def test_handle_users_api_error(
        self,
        mock_web_client,
        command,
        mock_workspace,
        mock_slack_conversations_response_final,
    ):
        """Test handling Slack API error when fetching users."""
        mock_workspaces = Mock()
        mock_workspaces.exists.return_value = True
        mock_workspaces.__iter__ = Mock(return_value=iter([mock_workspace]))

        mock_client = Mock()
        mock_web_client.return_value = mock_client

        mock_slack_conversations_response_final["response_metadata"] = {}
        mock_client.conversations_list.return_value = mock_slack_conversations_response_final

        slack_error = SlackApiError(
            message="API Error",
            response={"error": "invalid_auth"},
        )
        mock_client.users_list.side_effect = slack_error

        mock_conversation = Mock()

        stdout = StringIO()
        with (
            patch.object(Workspace.objects, "all", return_value=mock_workspaces),
            patch.object(Conversation, "update_data", return_value=mock_conversation),
            patch.object(Conversation, "bulk_save"),
        ):
            command.stdout = stdout
            command.handle(batch_size=1000, delay=0.5)

        output = stdout.getvalue()
        assert "Processing workspace: Test Workspace" in output
        assert "Populated 1 channels" in output
        assert "Failed to fetch members: invalid_auth" in output

    @patch("apps.slack.management.commands.slack_sync_data.WebClient")
    def test_handle_no_conversations_or_members(self, mock_web_client, command, mock_workspace):
        """Test handling when API returns empty results."""
        mock_workspaces = Mock()
        mock_workspaces.exists.return_value = True
        mock_workspaces.__iter__ = Mock(return_value=iter([mock_workspace]))

        mock_client = Mock()
        mock_web_client.return_value = mock_client

        empty_conversations_response = {
            "ok": True,
            "channels": [],
            "response_metadata": {},
        }
        empty_users_response = {
            "ok": True,
            "members": [],
            "response_metadata": {},
        }

        mock_client.conversations_list.return_value = empty_conversations_response
        mock_client.users_list.return_value = empty_users_response

        stdout = StringIO()
        with (
            patch.object(Workspace.objects, "all", return_value=mock_workspaces),
            patch.object(Conversation, "bulk_save") as mock_conv_bulk_save,
            patch.object(Member, "bulk_save") as mock_member_bulk_save,
        ):
            command.stdout = stdout
            command.handle(batch_size=1000, delay=0.5)

        mock_conv_bulk_save.assert_not_called()
        mock_member_bulk_save.assert_not_called()

        output = stdout.getvalue()
        assert "Processing workspace: Test Workspace" in output

    @patch("apps.slack.management.commands.slack_sync_data.WebClient")
    def test_handle_update_data_returns_none(
        self,
        mock_web_client,
        command,
        mock_workspace,
        mock_slack_conversations_response_final,
        mock_slack_users_response_final,
    ):
        """Test handling when update_data returns None."""
        mock_workspaces = Mock()
        mock_workspaces.exists.return_value = True
        mock_workspaces.__iter__ = Mock(return_value=iter([mock_workspace]))

        mock_client = Mock()
        mock_web_client.return_value = mock_client

        mock_slack_conversations_response_final["response_metadata"] = {}
        mock_slack_users_response_final["response_metadata"] = {}

        mock_client.conversations_list.return_value = mock_slack_conversations_response_final
        mock_client.users_list.return_value = mock_slack_users_response_final

        stdout = StringIO()
        with (
            patch.object(Workspace.objects, "all", return_value=mock_workspaces),
            patch.object(Conversation, "update_data", return_value=None),
            patch.object(Member, "update_data", return_value=None),
            patch.object(Conversation, "bulk_save") as mock_conv_bulk_save,
            patch.object(Member, "bulk_save") as mock_member_bulk_save,
        ):
            command.stdout = stdout
            command.handle(batch_size=1000, delay=0.5)

        mock_conv_bulk_save.assert_not_called()
        mock_member_bulk_save.assert_not_called()

    def test_handle_slack_response_with_invalid_response(self, command):
        """Test _handle_slack_response with invalid response."""
        stdout = StringIO()
        command.stdout = stdout

        response = {"ok": False}
        result = command._handle_slack_response(response, "test_method")

        assert result is None
        output = stdout.getvalue()
        assert "test_method API call failed" in output

    def test_handle_slack_response_with_valid_response(self, command):
        """Test _handle_slack_response with valid response."""
        response = {"ok": True, "data": "test"}
        result = command._handle_slack_response(response, "test_method")

        assert result is None

    def test_add_arguments(self, command):
        """Test add_arguments method."""
        parser = MagicMock()
        command.add_arguments(parser)

        assert parser.add_argument.call_count == CONSTANT_2

        parser.add_argument.assert_any_call(
            "--batch-size",
            type=int,
            default=1000,
            help="Number of conversations to retrieve per request",
        )

        parser.add_argument.assert_any_call(
            "--delay",
            type=float,
            default=0.5,
            help="Delay between API requests in seconds",
        )

    @patch("apps.slack.management.commands.slack_sync_data.WebClient")
    @patch("apps.slack.management.commands.slack_sync_data.time.sleep")
    def test_handle_with_custom_options(
        self,
        mock_sleep,
        mock_web_client,
        command,
        mock_workspace,
        mock_slack_conversations_response_final,
        mock_slack_users_response_final,
    ):
        """Test handle with custom batch_size and delay options."""
        mock_workspaces = Mock()
        mock_workspaces.exists.return_value = True
        mock_workspaces.__iter__ = Mock(return_value=iter([mock_workspace]))

        mock_client = Mock()
        mock_web_client.return_value = mock_client

        mock_slack_conversations_response_final["response_metadata"] = {}
        mock_slack_users_response_final["response_metadata"] = {}

        mock_client.conversations_list.return_value = mock_slack_conversations_response_final
        mock_client.users_list.return_value = mock_slack_users_response_final

        mock_conversation = Mock()
        mock_member = Mock()

        stdout = StringIO()
        with (
            patch.object(Workspace.objects, "all", return_value=mock_workspaces),
            patch.object(Conversation, "update_data", return_value=mock_conversation),
            patch.object(Member, "update_data", return_value=mock_member),
            patch.object(Conversation, "bulk_save"),
            patch.object(Member, "bulk_save"),
        ):
            command.stdout = stdout
            command.handle(batch_size=500, delay=1.0)

        mock_client.conversations_list.assert_called_once_with(
            cursor=None,
            exclude_archived=False,
            limit=500,
            timeout=30,
            types="public_channel,private_channel",
        )
        mock_client.users_list.assert_called_once_with(cursor=None, limit=500, timeout=30)

    def test_management_command_via_call_command(self):
        """Test running the command via Django's call_command."""
        stdout = StringIO()

        with (
            patch.object(Workspace.objects, "all") as mock_all,
            patch("builtins.print") as mock_print,
        ):
            mock_all.return_value.exists.return_value = False
            call_command("slack_sync_data", stdout=stdout)

        mock_print.assert_not_called()

    @patch("apps.slack.management.commands.slack_sync_data.WebClient")
    def test_handle_multiple_workspaces(
        self,
        mock_web_client,
        command,
        mock_slack_conversations_response_final,
        mock_slack_users_response_final,
    ):
        """Test handling multiple workspaces."""
        workspace1 = Mock(spec=Workspace)
        workspace1.__str__ = Mock(return_value="Workspace 1")
        workspace1.bot_token = TEST_TOKEN_1

        workspace2 = Mock(spec=Workspace)
        workspace2.__str__ = Mock(return_value="Workspace 2")
        workspace2.bot_token = TEST_TOKEN_2

        mock_workspaces = Mock()
        mock_workspaces.exists.return_value = True
        mock_workspaces.__iter__ = Mock(return_value=iter([workspace1, workspace2]))

        mock_client1 = Mock()
        mock_client2 = Mock()
        mock_web_client.side_effect = [mock_client1, mock_client2]

        mock_slack_conversations_response_final["response_metadata"] = {}
        mock_slack_users_response_final["response_metadata"] = {}

        mock_client1.conversations_list.return_value = mock_slack_conversations_response_final
        mock_client1.users_list.return_value = mock_slack_users_response_final
        mock_client2.conversations_list.return_value = mock_slack_conversations_response_final
        mock_client2.users_list.return_value = mock_slack_users_response_final

        mock_conversation = Mock()
        mock_member = Mock()

        stdout = StringIO()
        with (
            patch.object(Workspace.objects, "all", return_value=mock_workspaces),
            patch.object(Conversation, "update_data", return_value=mock_conversation),
            patch.object(Member, "update_data", return_value=mock_member),
            patch.object(Conversation, "bulk_save") as mock_conv_bulk_save,
            patch.object(Member, "bulk_save") as mock_member_bulk_save,
        ):
            command.stdout = stdout
            command.handle(batch_size=1000, delay=0.5)

        assert mock_web_client.call_count == CONSTANT_2
        mock_web_client.assert_any_call(token=TEST_TOKEN_1)
        mock_web_client.assert_any_call(token=TEST_TOKEN_2)

        assert mock_conv_bulk_save.call_count == CONSTANT_2
        assert mock_member_bulk_save.call_count == CONSTANT_2

        output = stdout.getvalue()
        assert "Processing workspace: Workspace 1" in output
        assert "Processing workspace: Workspace 2" in output

    @patch("apps.slack.management.commands.slack_sync_data.WebClient")
    @patch("apps.slack.management.commands.slack_sync_data.time.sleep")
    def test_handle_delay_zero_skips_sleep(
        self,
        mock_sleep,
        mock_web_client,
        command,
        mock_workspace,
        mock_slack_conversations_response,
        mock_slack_conversations_response_final,
        mock_slack_users_response_final,
    ):
        """Test that time.sleep is not called when delay=0."""
        mock_workspaces = Mock()
        mock_workspaces.exists.return_value = True
        mock_workspaces.__iter__ = Mock(return_value=iter([mock_workspace]))

        mock_client = Mock()
        mock_web_client.return_value = mock_client

        mock_client.conversations_list.side_effect = [
            mock_slack_conversations_response,
            mock_slack_conversations_response_final,
        ]
        mock_slack_users_response_final["response_metadata"] = {}
        mock_client.users_list.return_value = mock_slack_users_response_final

        mock_conversation = Mock()
        mock_member = Mock()

        stdout = StringIO()
        with (
            patch.object(Workspace.objects, "all", return_value=mock_workspaces),
            patch.object(Conversation, "update_data", return_value=mock_conversation),
            patch.object(Member, "update_data", return_value=mock_member),
            patch.object(Conversation, "bulk_save"),
            patch.object(Member, "bulk_save"),
        ):
            command.stdout = stdout
            command.handle(batch_size=1000, delay=0)

        mock_sleep.assert_not_called()

    @patch("apps.slack.management.commands.slack_sync_data.WebClient")
    def test_handle_conversations_api_error(
        self,
        mock_web_client,
        command,
        mock_workspace,
        mock_slack_users_response_final,
    ):
        """Test handling Slack API error when fetching conversations."""
        mock_workspaces = Mock()
        mock_workspaces.exists.return_value = True
        mock_workspaces.__iter__ = Mock(return_value=iter([mock_workspace]))

        mock_client = Mock()
        mock_web_client.return_value = mock_client

        slack_error = SlackApiError(
            message="API Error",
            response={"error": "invalid_auth"},
        )
        mock_client.conversations_list.side_effect = slack_error

        mock_slack_users_response_final["response_metadata"] = {}
        mock_client.users_list.return_value = mock_slack_users_response_final

        mock_member = Mock()

        stdout = StringIO()
        with (
            patch.object(Workspace.objects, "all", return_value=mock_workspaces),
            patch.object(Member, "update_data", return_value=mock_member),
            patch.object(Member, "bulk_save"),
        ):
            command.stdout = stdout
            command.handle(batch_size=1000, delay=0.5)

        output = stdout.getvalue()
        assert "Failed to fetch conversations: invalid_auth" in output
