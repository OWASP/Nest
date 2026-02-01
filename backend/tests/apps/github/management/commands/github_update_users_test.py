"""Tests for the github_update_users Django management command."""

from unittest.mock import MagicMock, patch

from django.core.management.base import BaseCommand

from apps.github.management.commands.github_update_users import Command


class TestGithubUpdateUsersCommand:
    def test_command_help_text(self):
        """Test that the command has the correct help text."""
        command = Command()
        assert command.help == "Update GitHub users."

    def test_command_inheritance(self):
        """Test that the command inherits from BaseCommand."""
        command = Command()

        assert isinstance(command, BaseCommand)

    def test_add_arguments(self):
        """Test that the command adds the correct arguments."""
        command = Command()
        parser = MagicMock()

        command.add_arguments(parser)

        parser.add_argument.assert_called_once_with(
            "--offset", default=0, required=False, type=int
        )

    @patch("apps.github.management.commands.github_update_users.call_command")
    @patch("apps.github.management.commands.github_update_users.User")
    @patch("apps.github.management.commands.github_update_users.RepositoryContributor")
    @patch("apps.github.management.commands.github_update_users.BATCH_SIZE", 2)
    def test_handle_with_default_offset(
        self, mock_repository_contributor, mock_user, mock_call_command
    ):
        """Test command execution with default offset."""
        mock_user1 = MagicMock(id=1, title="User 1", contributions_count=0)
        mock_user2 = MagicMock(id=2, title="User 2", contributions_count=0)
        mock_user3 = MagicMock(id=3, title="User 3", contributions_count=0)

        mock_users_queryset = MagicMock()
        mock_users_queryset.count.return_value = 3
        mock_users_queryset.__getitem__.return_value = [mock_user1, mock_user2, mock_user3]

        mock_user.objects.order_by.return_value = mock_users_queryset

        mock_rc_objects = MagicMock()
        mock_rc_objects.exclude.return_value.values.return_value.annotate.return_value = [
            {"user_id": 1, "total_contributions": 10},
            {"user_id": 2, "total_contributions": 20},
            {"user_id": 3, "total_contributions": 30},
        ]
        mock_repository_contributor.objects = mock_rc_objects

        with patch("builtins.print") as mock_print:
            command = Command()
            command.handle(offset=0)

        mock_user.objects.order_by.assert_called_once_with("-created_at")
        mock_users_queryset.count.assert_called_once()
        mock_users_queryset.__getitem__.assert_called_once_with(slice(0, None))

        mock_rc_objects.exclude.return_value.values.assert_called_once_with("user_id")
        mock_rc_objects.exclude.return_value.values.return_value.annotate.assert_called_once()

        assert mock_print.call_count == 3
        mock_print.assert_any_call("1 of 3     User 1")
        mock_print.assert_any_call("2 of 3     User 2")
        mock_print.assert_any_call("3 of 3     User 3")

        assert mock_user1.contributions_count == 10
        assert mock_user2.contributions_count == 20
        assert mock_user3.contributions_count == 30

        assert mock_user.bulk_save.call_count == 2
        assert mock_user.bulk_save.call_args_list[-1][0][0] == [mock_user1, mock_user2, mock_user3]

    @patch("apps.github.management.commands.github_update_users.call_command")
    @patch("apps.github.management.commands.github_update_users.User")
    @patch("apps.github.management.commands.github_update_users.RepositoryContributor")
    @patch("apps.github.management.commands.github_update_users.BATCH_SIZE", 2)
    def test_handle_with_custom_offset(
        self, mock_repository_contributor, mock_user, mock_call_command
    ):
        """Test command execution with custom offset."""
        mock_user1 = MagicMock(id=2, title="User 2", contributions_count=0)
        mock_user2 = MagicMock(id=3, title="User 3", contributions_count=0)

        mock_users_queryset = MagicMock()
        mock_users_queryset.count.return_value = 3
        mock_users_queryset.__getitem__.return_value = [mock_user1, mock_user2]

        mock_user.objects.order_by.return_value = mock_users_queryset

        mock_rc_queryset = MagicMock()
        mock_rc_queryset.exclude.return_value.values.return_value.annotate.return_value = [
            {"user_id": 2, "total_contributions": 20},
            {"user_id": 3, "total_contributions": 30},
        ]
        mock_repository_contributor.objects = mock_rc_queryset

        with patch("builtins.print") as mock_print:
            command = Command()
            command.handle(offset=1)

        mock_user.objects.order_by.assert_called_once_with("-created_at")
        mock_users_queryset.count.assert_called_once()
        mock_users_queryset.__getitem__.assert_called_once_with(slice(1, None))

        assert mock_print.call_count == 2
        mock_print.assert_any_call("2 of 2     User 2")
        mock_print.assert_any_call("3 of 2     User 3")

        assert mock_user1.contributions_count == 20
        assert mock_user2.contributions_count == 30

        assert mock_user.bulk_save.call_count == 2
        assert mock_user.bulk_save.call_args_list[-1][0][0] == [mock_user1, mock_user2]

    @patch("apps.github.management.commands.github_update_users.call_command")
    @patch("apps.github.management.commands.github_update_users.User")
    @patch("apps.github.management.commands.github_update_users.RepositoryContributor")
    @patch("apps.github.management.commands.github_update_users.BATCH_SIZE", 3)
    def test_handle_with_users_having_no_contributions(
        self, mock_repository_contributor, mock_user, mock_call_command
    ):
        """Test command execution when users have no contributions."""
        mock_user1 = MagicMock(id=1, title="User 1", contributions_count=0)
        mock_user2 = MagicMock(id=2, title="User 2", contributions_count=0)

        mock_users_queryset = MagicMock()
        mock_users_queryset.count.return_value = 2
        mock_users_queryset.__getitem__.return_value = [mock_user1, mock_user2]

        mock_user.objects.order_by.return_value = mock_users_queryset

        mock_rc_queryset = MagicMock()
        mock_rc_queryset.exclude.return_value.values.return_value.annotate.return_value = []
        mock_repository_contributor.objects = mock_rc_queryset

        with patch("builtins.print") as mock_print:
            command = Command()
            command.handle(offset=0)

        assert mock_print.call_count == 2
        mock_print.assert_any_call("1 of 2     User 1")
        mock_print.assert_any_call("2 of 2     User 2")

        assert mock_user1.contributions_count == 0
        assert mock_user2.contributions_count == 0

        assert mock_user.bulk_save.call_count == 1
        assert mock_user.bulk_save.call_args_list[-1][0][0] == [mock_user1, mock_user2]

    @patch("apps.github.management.commands.github_update_users.call_command")
    @patch("apps.github.management.commands.github_update_users.User")
    @patch("apps.github.management.commands.github_update_users.RepositoryContributor")
    @patch("apps.github.management.commands.github_update_users.BATCH_SIZE", 1)
    def test_handle_with_single_user(
        self, mock_repository_contributor, mock_user, mock_call_command
    ):
        """Test command execution with single user."""
        mock_user1 = MagicMock(id=1, title="User 1", contributions_count=0)

        mock_users_queryset = MagicMock()
        mock_users_queryset.count.return_value = 1
        mock_users_queryset.__getitem__.return_value = [mock_user1]

        mock_user.objects.order_by.return_value = mock_users_queryset

        mock_rc_queryset = MagicMock()
        mock_rc_queryset.exclude.return_value.values.return_value.annotate.return_value = [
            {"user_id": 1, "total_contributions": 15},
        ]
        mock_repository_contributor.objects = mock_rc_queryset

        with patch("builtins.print") as mock_print:
            command = Command()
            command.handle(offset=0)

        mock_print.assert_called_once_with("1 of 1     User 1")

        assert mock_user1.contributions_count == 15

        assert mock_user.bulk_save.call_count == 2
        assert mock_user.bulk_save.call_args_list[-1][0][0] == [mock_user1]

    @patch("apps.github.management.commands.github_update_users.call_command")
    @patch("apps.github.management.commands.github_update_users.User")
    @patch("apps.github.management.commands.github_update_users.RepositoryContributor")
    @patch("apps.github.management.commands.github_update_users.BATCH_SIZE", 2)
    def test_handle_with_empty_user_list(
        self, mock_repository_contributor, mock_user, mock_call_command
    ):
        """Test command execution with no users."""
        mock_users_queryset = MagicMock()
        mock_users_queryset.count.return_value = 0
        mock_users_queryset.__getitem__.return_value = []

        mock_user.objects.order_by.return_value = mock_users_queryset

        mock_rc_queryset = MagicMock()
        mock_rc_queryset.exclude.return_value.values.return_value.annotate.return_value = []
        mock_repository_contributor.objects = mock_rc_queryset

        with patch("builtins.print") as mock_print:
            command = Command()
            command.handle(offset=0)

        mock_print.assert_not_called()

        assert mock_user.bulk_save.call_count == 1
        assert mock_user.bulk_save.call_args_list[-1][0][0] == []

    @patch("apps.github.management.commands.github_update_users.call_command")
    @patch("apps.github.management.commands.github_update_users.User")
    @patch("apps.github.management.commands.github_update_users.RepositoryContributor")
    @patch("apps.github.management.commands.github_update_users.BATCH_SIZE", 2)
    def test_handle_with_exact_batch_size(
        self, mock_repository_contributor, mock_user, mock_call_command
    ):
        """Test command execution when user count equals batch size."""
        mock_user1 = MagicMock(id=1, title="User 1", contributions_count=0)
        mock_user2 = MagicMock(id=2, title="User 2", contributions_count=0)

        mock_users_queryset = MagicMock()
        mock_users_queryset.count.return_value = 2
        mock_users_queryset.__getitem__.return_value = [mock_user1, mock_user2]

        mock_user.objects.order_by.return_value = mock_users_queryset

        mock_rc_queryset = MagicMock()
        mock_rc_queryset.exclude.return_value.values.return_value.annotate.return_value = [
            {"user_id": 1, "total_contributions": 10},
            {"user_id": 2, "total_contributions": 20},
        ]
        mock_repository_contributor.objects = mock_rc_queryset

        with patch("builtins.print") as mock_print:
            command = Command()
            command.handle(offset=0)

        assert mock_print.call_count == 2
        mock_print.assert_any_call("1 of 2     User 1")
        mock_print.assert_any_call("2 of 2     User 2")

        assert mock_user1.contributions_count == 10
        assert mock_user2.contributions_count == 20

        assert mock_user.bulk_save.call_count == 2
        assert mock_user.bulk_save.call_args_list[-1][0][0] == [mock_user1, mock_user2]

    @patch("apps.github.management.commands.github_update_users.call_command")
    @patch("apps.github.management.commands.github_update_users.User")
    @patch("apps.github.management.commands.github_update_users.RepositoryContributor")
    def test_badge_sync_commands_are_called(
        self, mock_repository_contributor, mock_user, mock_call_command
    ):
        """Test that badge sync commands run after user update."""
        mock_users_queryset = MagicMock()
        mock_users_queryset.count.return_value = 0
        mock_users_queryset.__getitem__.return_value = []

        mock_user.objects.order_by.return_value = mock_users_queryset

        mock_rc_queryset = MagicMock()
        mock_rc_queryset.exclude.return_value.values.return_value.annotate.return_value = []
        mock_repository_contributor.objects = mock_rc_queryset

        command = Command()
        command.handle(offset=0)

        mock_call_command.assert_any_call("nest_update_staff_badges")
        mock_call_command.assert_any_call("nest_update_project_leader_badges")
