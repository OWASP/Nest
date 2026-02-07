from unittest.mock import MagicMock

from django.core.management import call_command
from slack_sdk.errors import SlackApiError

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
                {"user": "U1", "reply_count": 1, "ts": "123.001"},
                {"user": "U2", "ts": "123.002"},
            ],
            "response_metadata": {"next_cursor": ""},
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


class TestResolveGithubToSlack:
    """Tests for _resolve_github_to_slack method."""

    target_module = "apps.slack.management.commands.slack_sync_messages"

    def test_github_user_not_found(self, mocker):
        """Test handling when GitHub user doesn't exist."""
        mock_user = mocker.patch(f"{self.target_module}.User")
        mock_user.DoesNotExist = Exception
        mock_user.objects.get.side_effect = mock_user.DoesNotExist

        command = Command()
        command.stdout = MagicMock()
        command.stderr = MagicMock()

        result = command._resolve_github_to_slack("nonexistent_user")

        assert result is None
        command.stderr.write.assert_called_once()

    def test_member_profile_not_found(self, mocker):
        """Test handling when MemberProfile doesn't exist for user."""
        mock_user = mocker.patch(f"{self.target_module}.User")
        mock_profile = mocker.patch(f"{self.target_module}.MemberProfile")

        mock_user_instance = MagicMock()
        mock_user.objects.get.return_value = mock_user_instance
        mock_profile.DoesNotExist = Exception
        mock_profile.objects.get.side_effect = mock_profile.DoesNotExist

        command = Command()
        command.stdout = MagicMock()
        command.stderr = MagicMock()

        result = command._resolve_github_to_slack("user_without_profile")

        assert result is None
        command.stderr.write.assert_called_once()

    def test_no_slack_id_in_profile(self, mocker):
        """Test handling when profile has no Slack ID."""
        mock_user = mocker.patch(f"{self.target_module}.User")
        mock_profile = mocker.patch(f"{self.target_module}.MemberProfile")

        mock_user_instance = MagicMock()
        mock_user.objects.get.return_value = mock_user_instance

        mock_profile_instance = MagicMock()
        mock_profile_instance.owasp_slack_id = None
        mock_profile.objects.get.return_value = mock_profile_instance

        command = Command()
        command.stdout = MagicMock()
        command.stderr = MagicMock()

        result = command._resolve_github_to_slack("user_no_slack")

        assert result is None
        command.stderr.write.assert_called_once()

    def test_successful_resolution(self, mocker):
        """Test successful GitHub to Slack resolution."""
        mock_user = mocker.patch(f"{self.target_module}.User")
        mock_profile = mocker.patch(f"{self.target_module}.MemberProfile")

        mock_user_instance = MagicMock()
        mock_user.objects.get.return_value = mock_user_instance

        mock_profile_instance = MagicMock()
        mock_profile_instance.owasp_slack_id = "U12345"
        mock_profile.objects.get.return_value = mock_profile_instance

        command = Command()
        command.stdout = MagicMock()

        result = command._resolve_github_to_slack("valid_user")

        assert result == "U12345"


class TestSyncUserMessages:
    """Tests for _sync_user_messages method."""

    target_module = "apps.slack.management.commands.slack_sync_messages"

    def test_no_search_token(self, mocker):
        """Test handling when DJANGO_SLACK_SEARCH_TOKEN is not set."""
        mocker.patch.dict("os.environ", {}, clear=True)
        mocker.patch(f"{self.target_module}.os.environ.get", return_value="")

        command = Command()
        command.stdout = MagicMock()
        command.stderr = MagicMock()

        command._sync_user_messages("U123", None, None, 1.0, 3)

        command.stderr.write.assert_called_once()

    def test_no_workspaces(self, mocker):
        """Test handling when no workspaces exist."""
        mocker.patch(f"{self.target_module}.os.environ.get", return_value="xoxp-test-token")
        mocker.patch(f"{self.target_module}.WebClient")

        mock_workspace = mocker.patch(f"{self.target_module}.Workspace")
        mock_queryset = MagicMock()
        mock_queryset.exists.return_value = False
        mock_workspace.objects.all.return_value = mock_queryset

        command = Command()
        command.stdout = MagicMock()

        command._sync_user_messages("U123", None, None, 1.0, 3)

        command.stdout.write.assert_called()

    def test_no_messages_found(self, mocker):
        """Test handling when search returns no messages."""
        mocker.patch(f"{self.target_module}.os.environ.get", return_value="xoxp-test-token")

        mock_workspace = mocker.patch(f"{self.target_module}.Workspace")
        mock_workspace_instance = MagicMock()
        mock_workspace_instance.name = "Test Workspace"
        mock_queryset = MagicMock()
        mock_queryset.exists.return_value = True
        mock_queryset.__iter__.return_value = [mock_workspace_instance]
        mock_workspace.objects.all.return_value = mock_queryset

        mock_webclient = mocker.patch(f"{self.target_module}.WebClient")
        mock_client = MagicMock()
        mock_webclient.return_value = mock_client
        mock_client.search_messages.return_value = {
            "ok": True,
            "messages": {"matches": []},
        }

        command = Command()
        command.stdout = MagicMock()

        command._sync_user_messages("U123", "2024-01-01", "2024-12-31", 0.1, 3)

        mock_client.search_messages.assert_called_once()

    def test_rate_limit_handling(self, mocker):
        """Test rate limiting is handled with retries."""
        mocker.patch(f"{self.target_module}.os.environ.get", return_value="xoxp-test-token")
        mocker.patch(f"{self.target_module}.time.sleep")

        mock_workspace = mocker.patch(f"{self.target_module}.Workspace")
        mock_workspace_instance = MagicMock()
        mock_workspace_instance.name = "Test Workspace"
        mock_queryset = MagicMock()
        mock_queryset.exists.return_value = True
        mock_queryset.__iter__.return_value = [mock_workspace_instance]
        mock_workspace.objects.all.return_value = mock_queryset

        mock_webclient = mocker.patch(f"{self.target_module}.WebClient")
        mock_client = MagicMock()
        mock_webclient.return_value = mock_client

        rate_limit_error = SlackApiError(
            response={"ok": False, "error": "ratelimited", "headers": {"Retry-After": "1"}},
            message="Rate limited",
        )
        rate_limit_error.response = MagicMock()
        rate_limit_error.response.__getitem__ = lambda _self, key: (
            "ratelimited" if key == "error" else None
        )
        rate_limit_error.response.get.side_effect = lambda key, default=None: (
            "ratelimited" if key == "error" else default
        )
        rate_limit_error.response.headers = {"Retry-After": "1"}
        mock_client.search_messages.side_effect = [
            rate_limit_error,
            {"ok": True, "messages": {"matches": []}},
        ]

        command = Command()
        command.stdout = MagicMock()

        command._sync_user_messages("U123", None, None, 0.1, 3)

    def test_max_retries_exceeded(self, mocker):
        """Test handling when max retries are exceeded."""
        mocker.patch(f"{self.target_module}.os.environ.get", return_value="xoxp-test-token")
        mocker.patch(f"{self.target_module}.time.sleep")

        mock_workspace = mocker.patch(f"{self.target_module}.Workspace")
        mock_workspace_instance = MagicMock()
        mock_workspace_instance.name = "Test Workspace"
        mock_queryset = MagicMock()
        mock_queryset.exists.return_value = True
        mock_queryset.__iter__.return_value = [mock_workspace_instance]
        mock_workspace.objects.all.return_value = mock_queryset

        mock_webclient = mocker.patch(f"{self.target_module}.WebClient")
        mock_client = MagicMock()
        mock_webclient.return_value = mock_client

        rate_limit_error = SlackApiError(
            response={"ok": False, "error": "ratelimited"},
            message="Rate limited",
        )
        rate_limit_error.response = MagicMock()
        rate_limit_error.response.__getitem__ = lambda _self, key: (
            "ratelimited" if key == "error" else None
        )
        rate_limit_error.response.get.side_effect = lambda key, default=None: (
            "ratelimited" if key == "error" else default
        )
        rate_limit_error.response.headers = {"Retry-After": "1"}

        mock_client.search_messages.side_effect = rate_limit_error

        command = Command()
        command.stdout = MagicMock()
        command._sync_user_messages("U123", None, None, 0.1, 1)


class TestFetchReplies:
    """Tests for _fetch_replies method."""

    target_module_path = "apps.slack.management.commands.slack_sync_messages"

    def test_no_replies_found(self, mocker):
        """Test handles case when no replies are found."""
        mocker.patch(f"{self.target_module_path}.Message")

        mock_client = MagicMock()
        mock_client.conversations_replies.return_value = {"ok": True, "messages": []}

        mock_message = MagicMock()
        mock_message.conversation.slack_channel_id = "C123"
        mock_message.latest_reply = None
        mock_message.slack_message_id = "123.456"
        mock_message.url = "https://test.com"

        command = Command()
        command.stdout = MagicMock()

        command._fetch_replies(mock_client, mock_message, 1.0, 3)

        mock_client.conversations_replies.assert_called_once()

    def test_replies_saved(self, mocker):
        """Test replies are saved when found."""
        mock_message_model = mocker.patch(f"{self.target_module_path}.Message")

        mock_client = MagicMock()
        mock_client.conversations_replies.return_value = {
            "ok": True,
            "messages": [{"user": "U1", "ts": "123.789"}],
            "response_metadata": {"next_cursor": ""},
        }

        mock_message = MagicMock()
        mock_message.conversation.slack_channel_id = "C123"
        mock_message.latest_reply = None
        mock_message.slack_message_id = "123.456"
        mock_message.url = "https://test.com"

        command = Command()
        command.stdout = MagicMock()

        mock_reply = MagicMock()
        mocker.patch.object(command, "_create_message", return_value=mock_reply)

        command._fetch_replies(mock_client, mock_message, 1.0, 3)

        mock_message_model.bulk_save.assert_called_once()

    def test_slack_api_error_handling(self, mocker):
        """Test SlackApiError is handled gracefully."""
        mock_client = MagicMock()
        mock_client.conversations_replies.side_effect = SlackApiError(
            response={"ok": False, "error": "channel_not_found"},
            message="channel not found",
        )

        mock_message = MagicMock()
        mock_message.conversation.slack_channel_id = "C123"
        mock_message.latest_reply = None
        mock_message.slack_message_id = "123.456"
        mock_message.url = "https://test.com"

        command = Command()
        command.stdout = MagicMock()

        command._fetch_replies(mock_client, mock_message, 1.0, 3)

        command.stdout.write.assert_called()


class TestCreateMessage:
    """Tests for _create_message method."""

    target_module_path = "apps.slack.management.commands.slack_sync_messages"

    def test_create_message_with_existing_member(self, mocker):
        """Test creates message with existing member."""
        mock_member = mocker.patch(f"{self.target_module_path}.Member")
        mock_message_model = mocker.patch(f"{self.target_module_path}.Message")

        existing_member = MagicMock()
        mock_member.objects.get.return_value = existing_member

        mock_client = MagicMock()
        mock_conversation = MagicMock()
        message_data = {"user": "U123", "ts": "123.456"}

        command = Command()
        command.stdout = MagicMock()

        command._create_message(mock_client, message_data, mock_conversation, 1, 3)

        mock_message_model.update_data.assert_called_once_with(
            data=message_data,
            conversation=mock_conversation,
            author=existing_member,
            parent_message=None,
            save=False,
        )

    def test_create_message_no_user_id(self, mocker):
        """Test creates message without user lookup when no user ID."""
        mock_message_model = mocker.patch(f"{self.target_module_path}.Message")

        mock_client = MagicMock()
        mock_conversation = MagicMock()
        message_data = {"ts": "123.456", "text": "Test message"}

        command = Command()
        command.stdout = MagicMock()

        command._create_message(mock_client, message_data, mock_conversation, 1.0, 3)

        mock_message_model.update_data.assert_called_once_with(
            data=message_data,
            conversation=mock_conversation,
            author=None,
            parent_message=None,
            save=False,
        )

    def test_create_message_with_new_user(self, mocker):
        """Test creates new member when user doesn't exist."""
        mock_member = mocker.patch(f"{self.target_module_path}.Member")
        mocker.patch(f"{self.target_module_path}.Message")

        mock_member.DoesNotExist = Exception
        mock_member.objects.get.side_effect = mock_member.DoesNotExist

        mock_new_member = MagicMock()
        mock_member.update_data.return_value = mock_new_member

        mock_client = MagicMock()
        mock_client.users_info.return_value = {
            "ok": True,
            "user": {"id": "U123", "name": "newuser"},
        }

        mock_conversation = MagicMock()
        message_data = {"user": "U123", "ts": "123.456"}

        command = Command()
        command.stdout = MagicMock()

        command._create_message(mock_client, message_data, mock_conversation, 1, 3)

        mock_client.users_info.assert_called_once()

    def test_create_message_with_bot(self, mocker):
        """Test creates bot member when bot_id is present."""
        mock_member = mocker.patch(f"{self.target_module_path}.Member")
        mocker.patch(f"{self.target_module_path}.Message")

        mock_member.DoesNotExist = Exception
        mock_member.objects.get.side_effect = mock_member.DoesNotExist

        mock_new_member = MagicMock()
        mock_member.update_data.return_value = mock_new_member

        mock_client = MagicMock()
        mock_client.bots_info.return_value = {
            "ok": True,
            "bot": {"name": "Test Bot"},
        }

        mock_conversation = MagicMock()
        message_data = {"bot_id": "B123", "ts": "123.456"}

        command = Command()
        command.stdout = MagicMock()

        command._create_message(mock_client, message_data, mock_conversation, 1, 3)

        mock_client.bots_info.assert_called_once()

    def test_create_message_rate_limit_on_user_lookup(self, mocker):
        """Test handles rate limiting when looking up user info."""
        mock_member = mocker.patch(f"{self.target_module_path}.Member")
        mocker.patch(f"{self.target_module_path}.Message")
        mocker.patch(f"{self.target_module_path}.time.sleep")

        mock_member.DoesNotExist = Exception
        mock_member.objects.get.side_effect = mock_member.DoesNotExist

        mock_new_member = MagicMock()
        mock_member.update_data.return_value = mock_new_member

        rate_limit_error = SlackApiError(
            response={"ok": False, "error": "ratelimited"},
            message="Rate limited",
        )
        rate_limit_error.response = MagicMock()
        rate_limit_error.response.get = lambda key, default=None: (
            "ratelimited" if key == "error" else default
        )
        rate_limit_error.response.headers = MagicMock()
        rate_limit_error.response.headers.get = lambda _key, _default: 1

        mock_client = MagicMock()
        mock_client.users_info.side_effect = [
            rate_limit_error,
            {"ok": True, "user": {"id": "U123", "name": "testuser"}},
        ]

        mock_conversation = MagicMock()
        message_data = {"user": "U123", "ts": "123.456"}

        command = Command()
        command.stdout = MagicMock()

        command._create_message(mock_client, message_data, mock_conversation, 0.1, 3)


class TestHandleWithGithubUserId:
    """Tests for handle method with github_user_id option."""

    target_module = "apps.slack.management.commands.slack_sync_messages"

    def test_github_user_id_resolves_to_slack(self, mocker):
        """Test that github_user_id is resolved to slack_user_id."""
        mocker.patch(f"{self.target_module}.Workspace")

        command = Command()
        command.stdout = MagicMock()
        command.stderr = MagicMock()

        mock_resolve = mocker.patch.object(
            command, "_resolve_github_to_slack", return_value="U12345"
        )
        mock_sync = mocker.patch.object(command, "_sync_user_messages")

        command.handle(
            batch_size=999,
            channel_id=None,
            delay=4,
            max_retries=5,
            slack_user_id=None,
            github_user_id="test_github_user",
            start_at=None,
            end_at=None,
        )

        mock_resolve.assert_called_once_with("test_github_user")
        mock_sync.assert_called_once()

    def test_github_user_id_resolution_fails(self, mocker):
        """Test that execution stops when github_user_id resolution fails."""
        mocker.patch(f"{self.target_module}.Workspace")

        command = Command()
        command.stdout = MagicMock()
        command.stderr = MagicMock()

        mock_resolve = mocker.patch.object(command, "_resolve_github_to_slack", return_value=None)
        mock_sync = mocker.patch.object(command, "_sync_user_messages")

        command.handle(
            batch_size=999,
            channel_id=None,
            delay=4,
            max_retries=5,
            slack_user_id=None,
            github_user_id="nonexistent_user",
            start_at=None,
            end_at=None,
        )

        mock_resolve.assert_called_once()
        mock_sync.assert_not_called()


class TestFetchMessages:
    """Tests for _fetch_messages method."""

    target_module = "apps.slack.management.commands.slack_sync_messages"

    def test_rate_limit_handling(self, mocker):
        """Test rate limiting is handled in _fetch_messages."""
        mocker.patch(f"{self.target_module}.time.sleep")
        mock_conversation = MagicMock()
        mock_conversation.slack_channel_id = "C123"
        mock_conversation.latest_message = None

        mock_client = MagicMock()
        rate_limit_error = SlackApiError(
            response={"ok": False, "error": "ratelimited", "headers": {"Retry-After": "1"}},
            message="Rate limited",
        )
        rate_limit_error.response = MagicMock()
        rate_limit_error.response.__getitem__ = lambda _self, key: (
            "ratelimited" if key == "error" else None
        )
        rate_limit_error.response.get = lambda key, default=None: (
            "ratelimited" if key == "error" else default
        )
        rate_limit_error.response.headers = {"Retry-After": "1"}

        mock_client.conversations_history.side_effect = [
            rate_limit_error,
            {"ok": True, "messages": []},
        ]

        command = Command()
        command.stdout = MagicMock()

        command._fetch_messages(100, mock_client, mock_conversation, 0.1, 3)

        assert mock_client.conversations_history.call_count == 2
        command.stdout.write.assert_called()

    def test_max_retries_exceeded(self, mocker):
        """Test max retries exceeded in _fetch_messages."""
        mocker.patch(f"{self.target_module}.time.sleep")
        mock_conversation = MagicMock()
        mock_client = MagicMock()

        rate_limit_error = SlackApiError(
            response={"ok": False, "error": "ratelimited"},
            message="Rate limited",
        )
        rate_limit_error.response = MagicMock()
        rate_limit_error.response.__getitem__ = lambda _self, key: (
            "ratelimited" if key == "error" else None
        )
        rate_limit_error.response.get = lambda key, default=None: (
            "ratelimited" if key == "error" else default
        )
        rate_limit_error.response.headers = {"Retry-After": "1"}

        mock_client.conversations_history.side_effect = rate_limit_error

        command = Command()
        command.stdout = MagicMock()

        command._fetch_messages(100, mock_client, mock_conversation, 0.1, 1)

        assert mock_client.conversations_history.call_count == 2

    def test_generic_api_error(self, mocker):
        """Test generic API error in _fetch_messages."""
        mock_conversation = MagicMock()
        mock_client = MagicMock()

        error = SlackApiError(
            response={"ok": False, "error": "fatal_error"},
            message="Fatal error",
        )
        error.response = {"error": "fatal_error", "ok": False}

        mock_client.conversations_history.side_effect = error

        command = Command()
        command.stdout = MagicMock()

        command._fetch_messages(100, mock_client, mock_conversation, 0.1, 3)

        command.stdout.write.assert_called()


class TestSyncUserMessagesAdvanced:
    """Advanced tests for _sync_user_messages including date filtering."""

    target_module = "apps.slack.management.commands.slack_sync_messages"

    def test_date_filtering_and_pagination(self, mocker):
        """Test date filtering logic: skip future, process current, break on past."""
        mocker.patch(f"{self.target_module}.os.environ.get", return_value="token")
        mocker.patch(f"{self.target_module}.Workspace")
        mock_conversation_cls = mocker.patch(f"{self.target_module}.Conversation")
        mock_conversation_cls.objects.get_or_create.return_value = (MagicMock(), True)
        mock_msg_model = mocker.patch(f"{self.target_module}.Message")
        mock_queryset = MagicMock()
        mock_queryset.exists.return_value = True
        mock_queryset.__iter__.return_value = [MagicMock()]

        mock_workspace = MagicMock()
        mock_workspace.objects.all.return_value = mock_queryset
        mocker.patch(f"{self.target_module}.Workspace", mock_workspace)

        mock_client = MagicMock()
        mocker.patch(f"{self.target_module}.WebClient", return_value=mock_client)
        ts_future = "1704196800"
        ts_current = "1704110400"
        ts_past = "1704024000"

        mock_response = {
            "ok": True,
            "messages": {
                "matches": [
                    {"ts": ts_future, "channel": {"id": "C1"}},
                    {"ts": ts_current, "channel": {"id": "C1"}},
                    {"ts": ts_past, "channel": {"id": "C1"}},
                ]
            },
        }
        mock_client.search_messages.return_value = mock_response

        command = Command()
        command.stdout = MagicMock()
        mocker.patch.object(command, "_create_message", side_effect=lambda **_kwargs: MagicMock())

        command._sync_user_messages(
            "U1", start_at="2024-01-01", end_at="2024-01-02", delay=0, max_retries=1
        )
        mock_msg_model.bulk_save.assert_called()
        saved_list = mock_msg_model.bulk_save.call_args[0][0]
        assert len(saved_list) == 1

    def test_create_message_bot_failure(self, mocker):
        """Test _create_message handles bot info failure."""
        command = Command()
        command.stdout = MagicMock()

        mock_client = MagicMock()
        mock_client.bots_info.side_effect = SlackApiError(
            message="Error", response={"ok": False, "error": "fatal"}
        )

        mock_member = mocker.patch(f"{self.target_module}.Member")
        mock_member.DoesNotExist = Exception
        mock_member.objects.get.side_effect = Exception

        msg_data = {"bot_id": "B1"}

        mock_msg_model = mocker.patch(f"{self.target_module}.Message")

        command._create_message(mock_client, msg_data, MagicMock(), 0, 1)
        command.stdout.write.assert_called()
        mock_msg_model.update_data.assert_called_with(
            data=msg_data, conversation=mocker.ANY, author=None, parent_message=None, save=False
        )
