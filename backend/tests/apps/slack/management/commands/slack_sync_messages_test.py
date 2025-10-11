from unittest.mock import MagicMock

from django.core.management import call_command

from apps.slack.management.commands.slack_sync_messages import Command


class TestPopulateSlackMessages:
    """Unit tests for the slack_sync_messages command."""

    target_module = "apps.slack.management.commands.slack_sync_messages"

    def test_handle_command_flow(self, mocker):
        """Tests the entire command flow by mocking the ORM and Slack client."""
        mocker.patch(f"{self.target_module}.Member")
        mocker.patch(f"{self.target_module}.Message")

        mock_workspace = mocker.patch(f"{self.target_module}.Workspace")
        mock_conversation = mocker.patch(f"{self.target_module}.Conversation")
        mock_webclient = mocker.patch(f"{self.target_module}.WebClient")

        mock_workspace_instance = MagicMock()
        mock_value = "test-token"
        mock_workspace_instance.bot_token = mock_value
        mock_queryset = MagicMock()
        mock_queryset.exists.return_value = True
        mock_queryset.__iter__.return_value = [mock_workspace_instance]
        mock_workspace.objects.all.return_value = mock_queryset
        mock_conversation.objects.filter.return_value = [MagicMock()]

        mock_client_instance = MagicMock()
        mock_webclient.return_value = mock_client_instance

        mock_history_response = {
            "ok": True,
            "messages": [
                {"user": "U1", "reply_count": 1, "ts": "123.001"},  # Message WITH replies
                {"user": "U2", "ts": "123.002"},  # Message WITHOUT replies
            ],
            "response_metadata": {"next_cursor": ""},  # No more pages
        }
        mock_client_instance.conversations_history.return_value = mock_history_response
        mock_client_instance.conversations_replies.return_value = {"ok": True, "messages": []}
        mock_client_instance.users_info.return_value = {
            "ok": True,
            "user": {"id": "U1", "name": "testuser"},
        }

        mock_message_with_replies = MagicMock()
        mock_message_with_replies.has_replies = True
        mock_message_without_replies = MagicMock()
        mock_message_without_replies.has_replies = False

        mocker.patch.object(
            Command,
            "_create_message",
            side_effect=[mock_message_with_replies, mock_message_without_replies],
        )
        call_command("slack_sync_messages")
        mock_client_instance.conversations_history.assert_called_once()
        mock_client_instance.conversations_replies.assert_called_once()

    def test_handle_skips_workspace_without_token(self, mocker):
        """Tests that a workspace is skipped if it has no bot token."""
        mock_workspace = mocker.patch(f"{self.target_module}.Workspace")
        mock_webclient = mocker.patch(f"{self.target_module}.WebClient")

        mock_workspace_instance = MagicMock()
        mock_workspace_instance.bot_token = None

        mock_queryset = MagicMock()
        mock_queryset.exists.return_value = True
        mock_queryset.__iter__.return_value = [mock_workspace_instance]
        mock_workspace.objects.all.return_value = mock_queryset

        call_command("slack_sync_messages")
        mock_webclient.assert_not_called()

    def test_handle_slack_response_on_failure(self, mocker):
        """Tests that a non-OK Slack response is handled correctly."""
        mock_logger = mocker.patch(f"{self.target_module}.logger")
        mock_stdout = MagicMock()

        failed_response = {"ok": False, "error": "some_error"}

        command = Command()
        command.stdout = mock_stdout

        command._handle_slack_response(failed_response, "test_method")

        mock_logger.error.assert_called_once_with("test_method API call failed")
        mock_stdout.write.assert_called_once()
