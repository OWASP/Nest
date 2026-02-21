"""Tests for mentorship IssueUserInterest model."""

from unittest.mock import MagicMock

from apps.mentorship.models.issue_user_interest import IssueUserInterest


class TestIssueUserInterest:
    """Tests for IssueUserInterest model."""

    def test_str_returns_formatted_interest(self):
        """Test __str__ returns formatted interest string."""
        mock = MagicMock(spec=IssueUserInterest)
        mock.user = MagicMock(login="testuser")
        mock.issue = MagicMock(title="Fix bug #123")
        mock_module = MagicMock()
        mock_module.name = "Security Module"
        mock.module = mock_module

        result = IssueUserInterest.__str__(mock)

        assert result == "User [testuser] interested in 'Fix bug #123' for Security Module"
