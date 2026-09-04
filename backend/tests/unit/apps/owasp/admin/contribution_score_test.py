"""Tests for ContributionScore admin."""

from unittest.mock import MagicMock, Mock, patch

from django.contrib.admin.sites import AdminSite

from apps.owasp.admin.contribution_score import ContributionScoreAdmin
from apps.owasp.exceptions import CertificateIssuanceError
from apps.owasp.models.crp.contribution_score import ContributionScore

ADMIN_PATH = "apps.owasp.admin.contribution_score"


class TestContributionScoreAdmin:
    """Tests for ContributionScoreAdmin."""

    def setup_method(self):
        """Set up admin instance and mock request for each test."""
        self.admin = ContributionScoreAdmin(ContributionScore, AdminSite())
        self.request = Mock()

    def test_list_display(self):
        """Test list_display contains expected fields."""
        assert "github_user" in self.admin.list_display
        assert "value" in self.admin.list_display
        assert "tier" in self.admin.list_display

    def test_autocomplete_fields(self):
        """Test autocomplete_fields includes github_user."""
        assert "github_user" in self.admin.autocomplete_fields

    def test_search_fields(self):
        """Test search_fields includes github_user login and name."""
        assert "github_user__login" in self.admin.search_fields
        assert "github_user__name" in self.admin.search_fields

    def test_readonly_fields(self):
        """Test readonly_fields includes timestamp fields."""
        assert "nest_created_at" in self.admin.readonly_fields
        assert "nest_updated_at" in self.admin.readonly_fields

    def test_recalculate_short_description(self):
        """Test the recalculate action has the correct short description."""
        assert self.admin.recalculate.short_description == (
            "Recalculate selected contributors' scores"
        )

    @patch(f"{ADMIN_PATH}.ContributionScoreCalculator")
    def test_recalculate_all_success(self, mock_calculator_cls):
        """Test recalculate action when all users are recalculated successfully."""
        mock_calculator = MagicMock()
        mock_calculator_cls.return_value = mock_calculator

        score1 = Mock()
        score1.github_user.login = "user1"
        score2 = Mock()
        score2.github_user.login = "user2"
        queryset = [score1, score2]

        with patch.object(self.admin, "message_user") as mock_message_user:
            self.admin.recalculate(self.request, queryset)

        assert mock_calculator.recalculate_user.call_count == 2
        mock_message_user.assert_called_once_with(
            self.request,
            "Recalculated scores for 2 contributor(s). Failed for 0 contributor(s).",
        )

    @patch(f"{ADMIN_PATH}.ContributionScoreCalculator")
    def test_recalculate_all_fail(self, mock_calculator_cls):
        """Test recalculate action when all users fail recalculation."""
        mock_calculator = MagicMock()
        mock_calculator.recalculate_user.side_effect = ValueError("bad data")
        mock_calculator_cls.return_value = mock_calculator

        score1 = Mock()
        score1.github_user.login = "user1"
        queryset = [score1]

        with patch.object(self.admin, "message_user") as mock_message_user:
            self.admin.recalculate(self.request, queryset)

        mock_calculator.recalculate_user.assert_called_once_with(score1.github_user)
        mock_message_user.assert_called_once_with(
            self.request,
            "Recalculated scores for 0 contributor(s). Failed for 1 contributor(s).",
        )

    @patch(f"{ADMIN_PATH}.ContributionScoreCalculator")
    def test_recalculate_mixed_success_and_failure(self, mock_calculator_cls):
        """Test recalculate action with mixed success and failure results."""
        mock_calculator = MagicMock()
        mock_calculator_cls.return_value = mock_calculator

        score_ok = Mock()
        score_ok.github_user.login = "ok_user"

        score_fail = Mock()
        score_fail.github_user.login = "fail_user"

        def side_effect(user) -> None:
            if user == score_fail.github_user:
                error_msg = "type error"
                raise TypeError(error_msg)

        mock_calculator.recalculate_user.side_effect = side_effect
        queryset = [score_ok, score_fail]

        with patch.object(self.admin, "message_user") as mock_message_user:
            self.admin.recalculate(self.request, queryset)

        assert mock_calculator.recalculate_user.call_count == 2
        mock_message_user.assert_called_once_with(
            self.request,
            "Recalculated scores for 1 contributor(s). Failed for 1 contributor(s).",
        )

    @patch(f"{ADMIN_PATH}.ContributionScoreCalculator")
    def test_recalculate_sends_message_user(self, mock_calculator_cls):
        """Test recalculate calls message_user with correct summary string."""
        mock_calculator = MagicMock()
        mock_calculator_cls.return_value = mock_calculator

        score = Mock()
        score.github_user.login = "user1"
        queryset = [score]

        with patch.object(self.admin, "message_user") as mock_message_user:
            self.admin.recalculate(self.request, queryset)

        mock_message_user.assert_called_once_with(
            self.request,
            "Recalculated scores for 1 contributor(s). Failed for 0 contributor(s).",
        )

    @patch(f"{ADMIN_PATH}.ContributionScoreCalculator")
    def test_recalculate_failure_message_user(self, mock_calculator_cls):
        """Test recalculate calls message_user correctly when a user fails."""
        mock_calculator = MagicMock()
        mock_calculator.recalculate_user.side_effect = ValueError("oops")
        mock_calculator_cls.return_value = mock_calculator

        score = Mock()
        score.github_user.login = "bad_user"
        queryset = [score]

        with patch.object(self.admin, "message_user") as mock_message_user:
            self.admin.recalculate(self.request, queryset)

        mock_message_user.assert_called_once_with(
            self.request,
            "Recalculated scores for 0 contributor(s). Failed for 1 contributor(s).",
        )

    @patch(f"{ADMIN_PATH}.ContributionScoreCalculator")
    def test_recalculate_empty_queryset(self, mock_calculator_cls):
        """Test recalculate with an empty queryset sends zero-count message."""
        mock_calculator = MagicMock()
        mock_calculator_cls.return_value = mock_calculator

        with patch.object(self.admin, "message_user") as mock_message_user:
            self.admin.recalculate(self.request, [])

        mock_calculator.recalculate_user.assert_not_called()
        mock_message_user.assert_called_once_with(
            self.request,
            "Recalculated scores for 0 contributor(s). Failed for 0 contributor(s).",
        )

    @patch(f"{ADMIN_PATH}.ContributionScoreCalculator")
    def test_recalculate_certificate_issuance_error(self, mock_calculator_cls):
        """Test recalculate handles CertificateIssuanceError as a failure, continuing the loop."""
        mock_calculator = MagicMock()
        mock_calculator.recalculate_user.side_effect = CertificateIssuanceError
        mock_calculator_cls.return_value = mock_calculator

        score = Mock()
        score.github_user.login = "cert_error_user"
        queryset = [score]

        with patch.object(self.admin, "message_user") as mock_message_user:
            self.admin.recalculate(self.request, queryset)

        mock_calculator.recalculate_user.assert_called_once_with(score.github_user)
        mock_message_user.assert_called_once_with(
            self.request,
            "Recalculated scores for 0 contributor(s). Failed for 1 contributor(s).",
        )
