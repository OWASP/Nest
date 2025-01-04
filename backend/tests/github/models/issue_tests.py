from unittest.mock import Mock, patch

import pytest

from apps.github.models.issue import Issue
from apps.github.models.repository import Repository


class TestIssueModel:
    def test_open_issues_count(self):
        with patch("apps.github.models.issue.IndexBase.get_total_count") as mock_get_total_count:
            Issue.open_issues_count()
            mock_get_total_count.assert_called_once_with("issues")

    def test_bulk_save(self):
        mock_issues = [Mock(id=None), Mock(id=1)]
        with patch("apps.github.models.issue.BulkSaveModel.bulk_save") as mock_bulk_save:
            Issue.bulk_save(mock_issues, fields=["name"])
            mock_bulk_save.assert_called_once_with(Issue, mock_issues, fields=["name"])

    def test_repository_id(self):
        repository = Repository()
        issue = Issue(repository=repository)
        assert issue.repository_id == repository.id

    @patch("apps.github.models.issue.Issue.objects.get")
    def test_update_data_project_does_not_exist(self, mock_get):
        mock_get.side_effect = Issue.DoesNotExist
        gh_issue_mock = Mock()
        gh_issue_mock.raw_data = {"node_id": "12345"}

        with patch.object(Issue, "save", return_value=None) as mock_save:
            Issue.update_data(gh_issue_mock)
            mock_save.assert_called_once()

    @pytest.mark.parametrize(
        ("has_hint", "has_summary"),
        [
            (True, True),
            (False, True),
            (True, False),
            (False, False),
        ],
    )
    def test_save_method(self, has_hint, has_summary):
        issue = Issue()
        issue.generate_hint = Mock()
        issue.generate_summary = Mock()

        issue.hint = "Test Hint" if has_hint else None
        issue.summary = "Test Summary" if has_summary else None

        with patch("apps.github.models.issue.BulkSaveModel.save"):
            issue.save()

        if has_hint:
            issue.generate_hint.assert_not_called()
        else:
            issue.generate_hint.assert_called_once()

        if has_summary:
            issue.generate_summary.assert_not_called()
        else:
            issue.generate_summary.assert_called_once()
