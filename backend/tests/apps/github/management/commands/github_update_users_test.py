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

    @patch("apps.github.management.commands.github_update_users.get_scoring_context")
    @patch("apps.github.management.commands.github_update_users.compute_user_score")
    @patch("apps.github.management.commands.github_update_users.User")
    @patch("apps.github.management.commands.github_update_users.BATCH_SIZE", 2)
    def test_handle_with_default_offset(
        self,
        mock_user,
        mock_compute_score,
        mock_get_context,
    ):
        """Test command execution with default offset."""
        mock_user1 = MagicMock(id=1, title="User 1", contributions_count=0, is_owasp_staff=False)
        mock_user2 = MagicMock(id=2, title="User 2", contributions_count=0, is_owasp_staff=False)
        mock_user3 = MagicMock(id=3, title="User 3", contributions_count=0, is_owasp_staff=False)
        mock_user1.contribution_data = {}
        mock_user2.contribution_data = {}
        mock_user3.contribution_data = {}

        mock_users_queryset = MagicMock()
        mock_users_queryset.count.return_value = 3
        mock_sliced_qs = MagicMock()
        mock_sliced_qs.iterator.return_value = [mock_user1, mock_user2, mock_user3]
        mock_users_queryset.__getitem__.return_value = mock_sliced_qs

        mock_user.objects.order_by.return_value = mock_users_queryset

        mock_get_context.return_value = {
            "repo_data_map": {
                1: {"total_contributions": 10, "repo_count": 2},
                2: {"total_contributions": 20, "repo_count": 3},
                3: {"total_contributions": 30, "repo_count": 4},
            },
            "user_release_counts": {},
            "user_pr_flags": set(),
            "user_issue_flags": set(),
            "leadership_data": {},
            "board_members": set(),
            "gsoc_mentors": set(),
        }
        mock_compute_score.return_value = 42.0

        command = Command()
        command.stdout = MagicMock()
        command.handle(offset=0)

        mock_user.objects.order_by.assert_called_once_with("-created_at")
        mock_users_queryset.count.assert_called_once()
        mock_users_queryset.__getitem__.assert_called_once_with(slice(0, None))

        assert mock_user1.contributions_count == 10
        assert mock_user2.contributions_count == 20
        assert mock_user3.contributions_count == 30

        assert mock_user.bulk_save.call_count == 2
        assert mock_user.bulk_save.call_args_list[0][0][0] == [mock_user1, mock_user2]
        assert mock_user.bulk_save.call_args_list[1][0][0] == [mock_user3]

    @patch("apps.github.management.commands.github_update_users.get_scoring_context")
    @patch("apps.github.management.commands.github_update_users.compute_user_score")
    @patch("apps.github.management.commands.github_update_users.User")
    @patch("apps.github.management.commands.github_update_users.BATCH_SIZE", 2)
    def test_handle_with_custom_offset(
        self,
        mock_user,
        mock_compute_score,
        mock_get_context,
    ):
        """Test command execution with custom offset."""
        mock_user1 = MagicMock(id=2, title="User 2", contributions_count=0, is_owasp_staff=False)
        mock_user2 = MagicMock(id=3, title="User 3", contributions_count=0, is_owasp_staff=False)
        mock_user1.contribution_data = {}
        mock_user2.contribution_data = {}

        mock_users_queryset = MagicMock()
        mock_users_queryset.count.return_value = 3
        mock_sliced_qs = MagicMock()
        mock_sliced_qs.iterator.return_value = [mock_user1, mock_user2]
        mock_users_queryset.__getitem__.return_value = mock_sliced_qs

        mock_user.objects.order_by.return_value = mock_users_queryset

        mock_get_context.return_value = {
            "repo_data_map": {
                2: {"total_contributions": 20, "repo_count": 2},
                3: {"total_contributions": 30, "repo_count": 3},
            },
            "user_release_counts": {},
            "user_pr_flags": set(),
            "user_issue_flags": set(),
            "leadership_data": {},
            "board_members": set(),
            "gsoc_mentors": set(),
        }
        mock_compute_score.return_value = 42.0

        command = Command()
        command.stdout = MagicMock()
        command.handle(offset=1)

        mock_users_queryset.__getitem__.assert_called_once_with(slice(1, None))

        assert mock_user1.contributions_count == 20
        assert mock_user2.contributions_count == 30

        assert mock_user.bulk_save.call_count == 1
        assert mock_user.bulk_save.call_args_list[0][0][0] == [mock_user1, mock_user2]

    @patch("apps.github.management.commands.github_update_users.get_scoring_context")
    @patch("apps.github.management.commands.github_update_users.compute_user_score")
    @patch("apps.github.management.commands.github_update_users.User")
    @patch("apps.github.management.commands.github_update_users.BATCH_SIZE", 3)
    def test_handle_with_users_having_no_contributions(
        self,
        mock_user,
        mock_compute_score,
        mock_get_context,
    ):
        """Test command execution when users have no contributions."""
        mock_user1 = MagicMock(id=1, title="User 1", contributions_count=0, is_owasp_staff=False)
        mock_user2 = MagicMock(id=2, title="User 2", contributions_count=0, is_owasp_staff=False)
        mock_user1.contribution_data = {}
        mock_user2.contribution_data = {}

        mock_users_queryset = MagicMock()
        mock_users_queryset.count.return_value = 2
        mock_sliced_qs = MagicMock()
        mock_sliced_qs.iterator.return_value = [mock_user1, mock_user2]
        mock_users_queryset.__getitem__.return_value = mock_sliced_qs

        mock_user.objects.order_by.return_value = mock_users_queryset

        mock_get_context.return_value = {
            "repo_data_map": {},
            "user_release_counts": {},
            "user_pr_flags": set(),
            "user_issue_flags": set(),
            "leadership_data": {},
            "board_members": set(),
            "gsoc_mentors": set(),
        }
        mock_compute_score.return_value = 0.0

        command = Command()
        command.stdout = MagicMock()
        command.handle(offset=0)

        assert mock_user1.contributions_count == 0
        assert mock_user2.contributions_count == 0

    @patch("apps.github.management.commands.github_update_users.get_scoring_context")
    @patch("apps.github.management.commands.github_update_users.compute_user_score")
    @patch("apps.github.management.commands.github_update_users.User")
    @patch("apps.github.management.commands.github_update_users.BATCH_SIZE", 1)
    def test_handle_with_single_user(
        self,
        mock_user,
        mock_compute_score,
        mock_get_context,
    ):
        """Test command execution with single user."""
        mock_user1 = MagicMock(id=1, title="User 1", contributions_count=0, is_owasp_staff=False)
        mock_user1.contribution_data = {}

        mock_users_queryset = MagicMock()
        mock_users_queryset.count.return_value = 1
        mock_sliced_qs = MagicMock()
        mock_sliced_qs.iterator.return_value = [mock_user1]
        mock_users_queryset.__getitem__.return_value = mock_sliced_qs

        mock_user.objects.order_by.return_value = mock_users_queryset

        mock_get_context.return_value = {
            "repo_data_map": {
                1: {"total_contributions": 15, "repo_count": 2},
            },
            "user_release_counts": {},
            "user_pr_flags": set(),
            "user_issue_flags": set(),
            "leadership_data": {},
            "board_members": set(),
            "gsoc_mentors": set(),
        }
        mock_compute_score.return_value = 42.0

        command = Command()
        command.stdout = MagicMock()
        command.handle(offset=0)

        assert mock_user1.contributions_count == 15
        assert mock_user.bulk_save.call_count == 1
        assert mock_user.bulk_save.call_args_list[0][0][0] == [mock_user1]

    @patch("apps.github.management.commands.github_update_users.get_scoring_context")
    @patch("apps.github.management.commands.github_update_users.compute_user_score")
    @patch("apps.github.management.commands.github_update_users.User")
    @patch("apps.github.management.commands.github_update_users.BATCH_SIZE", 2)
    def test_handle_with_empty_user_list(
        self,
        mock_user,
        mock_compute_score,
        mock_get_context,
    ):
        """Test command execution with no users."""
        mock_users_queryset = MagicMock()
        mock_users_queryset.count.return_value = 0
        mock_sliced_qs = MagicMock()
        mock_sliced_qs.iterator.return_value = []
        mock_users_queryset.__getitem__.return_value = mock_sliced_qs

        mock_user.objects.order_by.return_value = mock_users_queryset

        mock_get_context.return_value = {
            "repo_data_map": {},
            "user_release_counts": {},
            "user_pr_flags": set(),
            "user_issue_flags": set(),
            "leadership_data": {},
            "board_members": set(),
            "gsoc_mentors": set(),
        }

        command = Command()
        command.stdout = MagicMock()
        command.handle(offset=0)

        assert mock_user.bulk_save.call_count == 0

    @patch("apps.github.management.commands.github_update_users.get_scoring_context")
    @patch("apps.github.management.commands.github_update_users.compute_user_score")
    @patch("apps.github.management.commands.github_update_users.User")
    @patch("apps.github.management.commands.github_update_users.BATCH_SIZE", 2)
    def test_handle_with_exact_batch_size(
        self,
        mock_user,
        mock_compute_score,
        mock_get_context,
    ):
        """Test command execution when user count equals batch size."""
        mock_user1 = MagicMock(id=1, title="User 1", contributions_count=0, is_owasp_staff=False)
        mock_user2 = MagicMock(id=2, title="User 2", contributions_count=0, is_owasp_staff=False)
        mock_user1.contribution_data = {}
        mock_user2.contribution_data = {}

        mock_users_queryset = MagicMock()
        mock_users_queryset.count.return_value = 2
        mock_sliced_qs = MagicMock()
        mock_sliced_qs.iterator.return_value = [mock_user1, mock_user2]
        mock_users_queryset.__getitem__.return_value = mock_sliced_qs

        mock_user.objects.order_by.return_value = mock_users_queryset

        mock_get_context.return_value = {
            "repo_data_map": {
                1: {"total_contributions": 10, "repo_count": 2},
                2: {"total_contributions": 20, "repo_count": 3},
            },
            "user_release_counts": {},
            "user_pr_flags": set(),
            "user_issue_flags": set(),
            "leadership_data": {},
            "board_members": set(),
            "gsoc_mentors": set(),
        }
        mock_compute_score.return_value = 42.0

        command = Command()
        command.stdout = MagicMock()
        command.handle(offset=0)

        assert mock_user1.contributions_count == 10
        assert mock_user2.contributions_count == 20
        assert mock_user.bulk_save.call_count == 1
        assert mock_user.bulk_save.call_args_list[0][0][0] == [mock_user1, mock_user2]

    @patch("apps.github.management.commands.github_update_users.get_scoring_context")
    @patch("apps.github.management.commands.github_update_users.compute_user_score")
    @patch("apps.github.management.commands.github_update_users.User")
    @patch("apps.github.management.commands.github_update_users.BATCH_SIZE", 2)
    def test_handle_with_leadership_data(
        self,
        mock_user,
        mock_compute_score,
        mock_get_context,
    ):
        """Test that leadership data flows into calculated_score."""
        mock_user1 = MagicMock(
            id=1,
            title="User 1",
            contributions_count=0,
            contribution_data=None,
        )

        mock_users_queryset = MagicMock()
        mock_users_queryset.count.return_value = 1
        mock_sliced_qs = MagicMock()
        mock_sliced_qs.iterator.return_value = [mock_user1]
        mock_users_queryset.__getitem__.return_value = mock_sliced_qs
        mock_user.objects.order_by.return_value = mock_users_queryset

        mock_get_context.return_value = {
            "repo_data_map": {
                1: {"total_contributions": 50, "repo_count": 3},
            },
            "user_release_counts": {},
            "user_pr_flags": set(),
            "user_issue_flags": set(),
            "leadership_data": {1: {"chapter_leader": 2, "project_leader": 1}},
            "board_members": set(),
            "gsoc_mentors": set(),
        }
        mock_compute_score.return_value = 55.0

        command = Command()
        command.stdout = MagicMock()
        command.handle(offset=0)

        assert mock_user1.contributions_count == 50
        assert mock_user1.calculated_score == 55.0
        assert mock_user.bulk_save.call_count == 1
        saved_fields = mock_user.bulk_save.call_args_list[0][1]["fields"]
        assert "calculated_score" in saved_fields
        assert "contributions_count" in saved_fields
