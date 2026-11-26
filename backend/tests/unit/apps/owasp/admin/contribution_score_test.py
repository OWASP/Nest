"""Tests for ContributionScore admin."""

from unittest.mock import MagicMock, Mock, call, patch

from django.contrib import messages
from django.contrib.admin.sites import AdminSite

from apps.owasp.admin.contribution_score import ContributionScoreAdmin
from apps.owasp.exceptions import CertificateIssuanceError
from apps.owasp.models.crp.contribution_score import ContributionScore

ADMIN_PATH = "apps.owasp.admin.contribution_score"


def _make_queryset(scores):
    """Return a mock queryset whose select_related() yields the given scores."""
    queryset = MagicMock()
    queryset.select_related.return_value = scores
    return queryset


def _make_score(login):
    """Return a mock ContributionScore for a GitHub user with the given login."""
    score = Mock()
    score.github_user.login = login
    return score


def _make_permission_request(*permissions):
    """Return a mock admin request whose user holds the given permission codenames."""
    granted = {f"owasp.{permission}" for permission in permissions}
    request = Mock()
    request.GET = {}
    request.user.has_perm.side_effect = lambda perm: perm in granted
    return request


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

    def test_recalculate_requires_change_permission(self):
        """Test the recalculate action declares the change permission."""
        assert list(self.admin.recalculate.allowed_permissions) == ["change"]

    def test_recalculate_hidden_without_change_permission(self):
        """Test the recalculate action is not offered to view-only staff."""
        request = _make_permission_request("view_contributionscore")

        assert "recalculate" not in self.admin.get_actions(request)

    def test_recalculate_offered_with_change_permission(self):
        """Test the recalculate action is offered to staff with change permission."""
        request = _make_permission_request("change_contributionscore")

        assert "recalculate" in self.admin.get_actions(request)

    @patch(f"{ADMIN_PATH}.ContributionScoreCalculator")
    def test_recalculate_selects_related_github_user(self, mock_calculator_cls):
        """Test recalculate loads GitHub users with the selected scores."""
        queryset = _make_queryset([])

        with patch.object(self.admin, "message_user"):
            self.admin.recalculate(self.request, queryset)

        queryset.select_related.assert_called_once_with("github_user")

    @patch(f"{ADMIN_PATH}.ContributionScoreCalculator")
    def test_recalculate_all_success(self, mock_calculator_cls):
        """Test recalculate action when all users are recalculated successfully."""
        mock_calculator = MagicMock()
        mock_calculator_cls.return_value = mock_calculator

        score1 = _make_score("user1")
        score2 = _make_score("user2")
        queryset = _make_queryset([score1, score2])

        with patch.object(self.admin, "message_user") as mock_message_user:
            self.admin.recalculate(self.request, queryset)

        mock_calculator.recalculate_user.assert_has_calls(
            [call(score1.github_user), call(score2.github_user)]
        )
        assert mock_calculator.recalculate_user.call_count == 2
        mock_message_user.assert_called_once_with(
            self.request,
            "Recalculated scores for 2 contributor(s). Failed for 0 contributor(s).",
            level=messages.INFO,
        )

    @patch(f"{ADMIN_PATH}.ContributionScoreCalculator")
    def test_recalculate_all_fail(self, mock_calculator_cls):
        """Test recalculate action when all users fail recalculation."""
        mock_calculator = MagicMock()
        mock_calculator.recalculate_user.side_effect = ValueError("bad data")
        mock_calculator_cls.return_value = mock_calculator

        score1 = _make_score("user1")
        queryset = _make_queryset([score1])

        with patch.object(self.admin, "message_user") as mock_message_user:
            self.admin.recalculate(self.request, queryset)

        mock_calculator.recalculate_user.assert_called_once_with(score1.github_user)
        mock_message_user.assert_called_once_with(
            self.request,
            "Recalculated scores for 0 contributor(s). Failed for 1 contributor(s).",
            level=messages.WARNING,
        )

    @patch(f"{ADMIN_PATH}.ContributionScoreCalculator")
    def test_recalculate_mixed_success_and_failure(self, mock_calculator_cls):
        """Test recalculate action with mixed success and failure results."""
        mock_calculator = MagicMock()
        mock_calculator_cls.return_value = mock_calculator

        score_ok = _make_score("ok_user")
        score_fail = _make_score("fail_user")

        def side_effect(user) -> None:
            if user == score_fail.github_user:
                error_msg = "type error"
                raise TypeError(error_msg)

        mock_calculator.recalculate_user.side_effect = side_effect
        queryset = _make_queryset([score_ok, score_fail])

        with patch.object(self.admin, "message_user") as mock_message_user:
            self.admin.recalculate(self.request, queryset)

        assert mock_calculator.recalculate_user.call_count == 2
        mock_message_user.assert_called_once_with(
            self.request,
            "Recalculated scores for 1 contributor(s). Failed for 1 contributor(s).",
            level=messages.WARNING,
        )

    @patch(f"{ADMIN_PATH}.ContributionScoreCalculator")
    def test_recalculate_unexpected_exception_does_not_abort_loop(self, mock_calculator_cls):
        """Test an unexpected error is counted as a failure and later users are processed."""
        mock_calculator = MagicMock()
        mock_calculator.recalculate_user.side_effect = [RuntimeError("database gone"), None]
        mock_calculator_cls.return_value = mock_calculator

        score_error = _make_score("error_user")
        score_ok = _make_score("ok_user")
        queryset = _make_queryset([score_error, score_ok])

        with (
            patch(f"{ADMIN_PATH}.logger") as mock_logger,
            patch.object(self.admin, "message_user") as mock_message_user,
        ):
            self.admin.recalculate(self.request, queryset)

        mock_calculator.recalculate_user.assert_has_calls(
            [call(score_error.github_user), call(score_ok.github_user)]
        )
        mock_logger.exception.assert_called_once_with(
            "Failed to recalculate score for user %s", "error_user"
        )
        mock_message_user.assert_called_once_with(
            self.request,
            "Recalculated scores for 1 contributor(s). Failed for 1 contributor(s).",
            level=messages.WARNING,
        )

    @patch(f"{ADMIN_PATH}.ContributionScoreCalculator")
    def test_recalculate_sends_message_user(self, mock_calculator_cls):
        """Test recalculate calls message_user with correct summary string."""
        mock_calculator = MagicMock()
        mock_calculator_cls.return_value = mock_calculator

        queryset = _make_queryset([_make_score("user1")])

        with patch.object(self.admin, "message_user") as mock_message_user:
            self.admin.recalculate(self.request, queryset)

        mock_message_user.assert_called_once_with(
            self.request,
            "Recalculated scores for 1 contributor(s). Failed for 0 contributor(s).",
            level=messages.INFO,
        )

    @patch(f"{ADMIN_PATH}.ContributionScoreCalculator")
    def test_recalculate_failure_message_user(self, mock_calculator_cls):
        """Test recalculate calls message_user correctly when a user fails."""
        mock_calculator = MagicMock()
        mock_calculator.recalculate_user.side_effect = ValueError("oops")
        mock_calculator_cls.return_value = mock_calculator

        queryset = _make_queryset([_make_score("bad_user")])

        with patch.object(self.admin, "message_user") as mock_message_user:
            self.admin.recalculate(self.request, queryset)

        mock_message_user.assert_called_once_with(
            self.request,
            "Recalculated scores for 0 contributor(s). Failed for 1 contributor(s).",
            level=messages.WARNING,
        )

    @patch(f"{ADMIN_PATH}.ContributionScoreCalculator")
    def test_recalculate_empty_queryset(self, mock_calculator_cls):
        """Test recalculate with an empty queryset sends zero-count message."""
        mock_calculator = MagicMock()
        mock_calculator_cls.return_value = mock_calculator

        with patch.object(self.admin, "message_user") as mock_message_user:
            self.admin.recalculate(self.request, _make_queryset([]))

        mock_calculator.recalculate_user.assert_not_called()
        mock_message_user.assert_called_once_with(
            self.request,
            "Recalculated scores for 0 contributor(s). Failed for 0 contributor(s).",
            level=messages.INFO,
        )

    @patch(f"{ADMIN_PATH}.ContributionScoreCalculator")
    def test_recalculate_certificate_issuance_error(self, mock_calculator_cls):
        """Test a certificate failure counts the score as updated and warns about it."""
        mock_calculator = MagicMock()
        mock_calculator.recalculate_user.side_effect = CertificateIssuanceError
        mock_calculator_cls.return_value = mock_calculator

        score = _make_score("cert_error_user")
        queryset = _make_queryset([score])

        with (
            patch(f"{ADMIN_PATH}.logger") as mock_logger,
            patch.object(self.admin, "message_user") as mock_message_user,
        ):
            self.admin.recalculate(self.request, queryset)

        mock_calculator.recalculate_user.assert_called_once_with(score.github_user)
        mock_logger.exception.assert_called_once_with(
            "Failed to issue certificate for user %s", "cert_error_user"
        )
        mock_message_user.assert_called_once_with(
            self.request,
            "Recalculated scores for 1 contributor(s). Failed for 0 contributor(s). "
            "Certificate issuance failed for 1 contributor(s).",
            level=messages.WARNING,
        )

    @patch(f"{ADMIN_PATH}.ContributionScoreCalculator")
    def test_recalculate_mixed_certificate_and_recalculation_failures(self, mock_calculator_cls):
        """Test the summary separates recalculation failures from certificate failures."""
        mock_calculator = MagicMock()
        mock_calculator.recalculate_user.side_effect = [
            None,
            CertificateIssuanceError,
            ValueError("bad data"),
        ]
        mock_calculator_cls.return_value = mock_calculator

        queryset = _make_queryset(
            [_make_score("ok_user"), _make_score("cert_user"), _make_score("bad_user")]
        )

        with patch.object(self.admin, "message_user") as mock_message_user:
            self.admin.recalculate(self.request, queryset)

        assert mock_calculator.recalculate_user.call_count == 3
        mock_message_user.assert_called_once_with(
            self.request,
            "Recalculated scores for 2 contributor(s). Failed for 1 contributor(s). "
            "Certificate issuance failed for 1 contributor(s).",
            level=messages.WARNING,
        )
