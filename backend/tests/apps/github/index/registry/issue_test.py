
from unittest.mock import MagicMock, patch

import pytest

from apps.github.index.registry.issue import IssueIndex
from apps.github.models.issue import Issue


@pytest.fixture
def issue_index(mocker):
    """Returns an instance of the IssueIndex."""
    mocker.patch("apps.common.index.IndexBase.__init__", return_value=None)
    return IssueIndex()


class TestIssueIndex:
    def test_class_attributes(self):
        """Test that the basic class attributes are set correctly."""
        assert IssueIndex.index_name == "issues"
        assert IssueIndex.should_index == "is_indexable"
        assert isinstance(IssueIndex.fields, tuple)
        assert len(IssueIndex.fields) > 0
        assert isinstance(IssueIndex.settings, dict)
        assert "attributesForFaceting" in IssueIndex.settings

    @patch("apps.common.index.IndexBase.reindex_synonyms")
    def test_update_synonyms(self, mock_reindex_synonyms):
        """Test that update_synonyms calls the parent method with correct args."""
        IssueIndex.update_synonyms()
        mock_reindex_synonyms.assert_called_once_with("github", "issues")

    def test_get_entities(self, issue_index):
        """
        Test that get_entities constructs the correct queryset by chaining
        the expected manager methods.
        """
        
        mock_open_issues_manager = MagicMock()
        mock_assignable_manager = MagicMock()
        mock_open_issues_manager.assignable = mock_assignable_manager

        mock_assignable_manager.select_related.return_value = MagicMock()
        mock_assignable_manager.select_related.return_value.prefetch_related.return_value = (
            "final_queryset"
        )

        with patch.object(Issue, "open_issues", mock_open_issues_manager):
            queryset = issue_index.get_entities()
            mock_assignable_manager.select_related.assert_called_once_with("repository")
            mock_assignable_manager.select_related.return_value.prefetch_related.assert_called_once_with(
                "assignees",
                "labels",
                "repository__project_set",
            )
            assert queryset == "final_queryset"
