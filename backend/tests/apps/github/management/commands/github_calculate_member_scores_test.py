"""Tests for github_calculate_member_scores management command."""

from unittest.mock import MagicMock, patch

from apps.github.management.commands.github_calculate_member_scores import Command


class TestCalculateMemberScoresCommand:
    """Test suite for the calculate member scores command."""

    @patch("apps.github.management.commands.github_calculate_member_scores.get_scoring_context")
    @patch("apps.github.management.commands.github_calculate_member_scores.compute_user_score")
    @patch("apps.github.management.commands.github_calculate_member_scores.User")
    @patch("apps.github.management.commands.github_calculate_member_scores.BATCH_SIZE", 100)
    def test_handle_all_users(
        self,
        mock_user_model,
        mock_compute_score,
        mock_get_context,
    ):
        """Test command processes all users."""
        mock_user_1 = MagicMock(id=1, is_owasp_staff=False)
        mock_user_1.contribution_data = {}
        mock_user_2 = MagicMock(id=2, is_owasp_staff=False)
        mock_user_2.contribution_data = {}

        mock_qs = MagicMock()
        mock_qs.count.return_value = 2
        mock_qs.iterator.return_value = [mock_user_1, mock_user_2]
        mock_qs.exists.return_value = True
        mock_user_model.objects.all.return_value = mock_qs

        mock_get_context.return_value = {
            "repo_data_map": {},
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
        command.style = MagicMock()
        command.style.SUCCESS = lambda x: x

        command.handle(user=None)

        mock_user_model.objects.all.assert_called_once()
        mock_user_model.bulk_save.assert_called()

    @patch("apps.github.management.commands.github_calculate_member_scores.get_scoring_context")
    @patch("apps.github.management.commands.github_calculate_member_scores.compute_user_score")
    @patch("apps.github.management.commands.github_calculate_member_scores.User")
    @patch("apps.github.management.commands.github_calculate_member_scores.BATCH_SIZE", 100)
    def test_handle_specific_user(
        self,
        mock_user_model,
        mock_compute_score,
        mock_get_context,
    ):
        """Test command processes a specific user."""
        mock_user = MagicMock(id=1, is_owasp_staff=False)
        mock_user.contribution_data = {}

        mock_qs = MagicMock()
        mock_qs.exists.return_value = True
        mock_qs.count.return_value = 1
        mock_qs.iterator.return_value = [mock_user]
        mock_user_model.objects.filter.return_value = mock_qs

        mock_get_context.return_value = {
            "repo_data_map": {},
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
        command.style = MagicMock()
        command.style.SUCCESS = lambda x: x

        command.handle(user="testuser")

        mock_user_model.objects.filter.assert_called_once_with(login="testuser")

    @patch("apps.github.management.commands.github_calculate_member_scores.User")
    def test_handle_user_not_found(self, mock_user_model):
        """Test command handles missing user gracefully."""
        mock_qs = MagicMock()
        mock_qs.exists.return_value = False
        mock_user_model.objects.filter.return_value = mock_qs

        command = Command()
        command.stdout = MagicMock()
        command.style = MagicMock()
        command.style.ERROR = lambda x: x

        command.handle(user="nonexistent")

        mock_user_model.bulk_save.assert_not_called()
        command.stdout.write.assert_called_once_with("Member 'nonexistent' not found")

    def test_add_arguments(self):
        """Test that the command adds the --user argument."""
        command = Command()
        parser = MagicMock()

        command.add_arguments(parser)

        parser.add_argument.assert_called_once_with(
            "--user",
            type=str,
            help="Specific user login to process",
        )

    @patch("apps.github.management.commands.github_calculate_member_scores.get_scoring_context")
    @patch("apps.github.management.commands.github_calculate_member_scores.compute_user_score")
    @patch("apps.github.management.commands.github_calculate_member_scores.User")
    @patch("apps.github.management.commands.github_calculate_member_scores.BATCH_SIZE", 2)
    def test_handle_batch_boundary(
        self,
        mock_user_model,
        mock_compute_score,
        mock_get_context,
    ):
        """Test batch processing when user count exceeds batch size."""
        mock_users = [
            MagicMock(id=i, is_owasp_staff=False, contribution_data={}) for i in range(5)
        ]

        mock_qs = MagicMock()
        mock_qs.count.return_value = 5
        mock_qs.iterator.return_value = mock_users
        mock_user_model.objects.all.return_value = mock_qs

        mock_get_context.return_value = {
            "repo_data_map": {},
            "user_release_counts": {},
            "user_pr_flags": set(),
            "user_issue_flags": set(),
            "leadership_data": {},
            "board_members": set(),
            "gsoc_mentors": set(),
        }
        mock_compute_score.return_value = 10.0

        command = Command()
        command.stdout = MagicMock()
        command.style = MagicMock()
        command.style.SUCCESS = lambda x: x

        command.handle(user=None)
        assert mock_user_model.bulk_save.call_count == 3
