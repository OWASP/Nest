from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.common.index import IndexBase
from apps.github.index.issue import IssueIndex
from apps.github.models.issue import Issue


class TestIssueIndex(SimpleTestCase):
    """Test the IssueIndex class."""

    databases = []

    def setUp(self):
        self.model = MagicMock()
        self.client = MagicMock()
        self.settings = MagicMock()
        self.issue_index = IssueIndex(self.model, self.client, self.settings)

    @patch("apps.common.index.IndexBase.reindex_synonyms")
    def test_update_synonyms(self, mock_reindex_synonyms):
        with patch.object(IndexBase, "get_client", return_value=self.client):
            IssueIndex.update_synonyms()
            mock_reindex_synonyms.assert_called_once_with("github", "issues")

    def test_get_entities(self):
        mock_assignable = MagicMock()
        mock_select_related = MagicMock()
        mock_prefetch_related = MagicMock()
        mock_open_issues = MagicMock()
        mock_open_issues.assignable = mock_assignable
        mock_assignable.select_related.return_value = mock_select_related
        mock_select_related.prefetch_related.return_value = mock_prefetch_related

        with patch.object(Issue, "open_issues", mock_open_issues):
            result = self.issue_index.get_entities()

            mock_assignable.select_related.assert_called_once_with("repository")
            mock_select_related.prefetch_related.assert_called_once_with(
                "assignees",
                "labels",
                "repository__project_set",
            )
            assert result == mock_prefetch_related
