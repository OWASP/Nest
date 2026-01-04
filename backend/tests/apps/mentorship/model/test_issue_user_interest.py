import pytest
from unittest.mock import MagicMock, patch

from apps.mentorship.models import IssueUserInterest, Module
from apps.github.models import Issue, User


class TestIssueUserInterest:
    user = MagicMock(spec=User, login="testuser")
    issue = MagicMock(spec=Issue, title="Test Issue")
    module = MagicMock(spec=Module, name="Test Module")

    @patch("apps.mentorship.models.IssueUserInterest.objects.create")
    def test_create_issue_user_interest(self, mock_create):
        mock_instance = MagicMock(spec=IssueUserInterest)
        mock_instance.user = self.user
        mock_instance.issue = self.issue
        mock_instance.module = self.module
        mock_instance.__str__.return_value = (
            f"User [{self.user.login}] interested in "
            f"'{self.issue.title}' for {self.module.name}"
        )

        mock_create.return_value = mock_instance

        interest = IssueUserInterest.objects.create(
            user=self.user,
            issue=self.issue,
            module=self.module,
        )

        mock_create.assert_called_once_with(
            user=self.user,
            issue=self.issue,
            module=self.module,
        )
        assert interest.user == self.user
        assert interest.issue == self.issue
        assert interest.module == self.module
        assert str(interest) == (
            f"User [{self.user.login}] interested in "
            f"'{self.issue.title}' for {self.module.name}"
        )

    @patch("apps.mentorship.models.IssueUserInterest.objects.create")
    def test_unique_together_constraint(self, mock_create):
        class MockIntegrityError(Exception):
            pass

        mock_create.side_effect = [
            MagicMock(),
            MockIntegrityError("Mock Integrity Error"),
        ]

        IssueUserInterest.objects.create(
            user=self.user,
            issue=self.issue,
            module=self.module,
        )

        with pytest.raises(MockIntegrityError):
            IssueUserInterest.objects.create(
                user=self.user,
                issue=self.issue,
                module=self.module,
            )

        assert mock_create.call_count == 2
