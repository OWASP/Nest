"""Tests for github_calculate_member_scores management command."""

from unittest.mock import MagicMock, patch

from apps.github.management.commands.github_calculate_member_scores import Command


class TestCalculateMemberScoresCommand:
    """Test suite for the calculate member scores command."""

    @patch("apps.github.management.commands.github_calculate_member_scores.User")
    @patch("apps.github.management.commands.github_calculate_member_scores.MemberScoreCalculator")
    def test_handle_all_users(self, mock_calculator_class, mock_user_model):
        """Test command processes all users with contributions."""
        mock_calculator = MagicMock()
        mock_calculator.calculate.return_value = 42.5
        mock_calculator_class.return_value = mock_calculator

        mock_user_1 = MagicMock()
        mock_user_2 = MagicMock()

        mock_qs = MagicMock()
        mock_qs.count.return_value = 2
        mock_qs.iterator.return_value = [mock_user_1, mock_user_2]
        mock_user_model.objects.filter.return_value = mock_qs

        command = Command()
        command.stdout = MagicMock()
        command.style = MagicMock()
        command.style.SUCCESS = lambda x: x

        command.handle(user=None)

        mock_user_model.objects.filter.assert_called_once_with(contributions_count__gt=0)
        assert mock_calculator.calculate.call_count == 2
        assert mock_user_1.calculated_score == 42.5
        assert mock_user_2.calculated_score == 42.5
        mock_user_model.bulk_save.assert_called()

    @patch("apps.github.management.commands.github_calculate_member_scores.User")
    @patch("apps.github.management.commands.github_calculate_member_scores.MemberScoreCalculator")
    def test_handle_specific_user(self, mock_calculator_class, mock_user_model):
        """Test command processes a specific user."""
        mock_calculator = MagicMock()
        mock_calculator.calculate.return_value = 55
        mock_calculator_class.return_value = mock_calculator

        mock_user = MagicMock()
        mock_qs = MagicMock()
        mock_qs.exists.return_value = True
        mock_qs.count.return_value = 1
        mock_qs.iterator.return_value = [mock_user]
        mock_user_model.objects.filter.return_value = mock_qs

        command = Command()
        command.stdout = MagicMock()
        command.style = MagicMock()
        command.style.SUCCESS = lambda x: x

        command.handle(user="testuser")

        mock_user_model.objects.filter.assert_called_once_with(login="testuser")
        assert mock_user.calculated_score == 55

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
