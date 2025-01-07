from unittest.mock import MagicMock, patch

import pytest

from apps.common.management.commands.algolia_update_synonyms import Command


@pytest.mark.parametrize(
    "indexes",
    [["IssueIndex", "ProjectIndex"]],
)
class TestAlgoliaUpdateSynonyms:
    @patch("builtins.print")
    @patch("apps.common.management.commands.algolia_update_synonyms.ProjectIndex")
    @patch("apps.common.management.commands.algolia_update_synonyms.IssueIndex")
    def test_handle(self, mock_issue_index, mock_project_index, mock_print, indexes):
        mock_indexes = {
            "IssueIndex": mock_issue_index,
            "ProjectIndex": mock_project_index,
        }
        for index_name, index_instance in mock_indexes.items():
            index_instance.update_synonyms = MagicMock()
            index_instance.index_name = index_name

        command = Command()
        command.handle()

        for index_name in indexes:
            index_instance = mock_indexes[index_name]
            index_instance.update_synonyms.assert_called_once()
            mock_print.assert_any_call(f"Updated {index_name.capitalize()} synonyms")
