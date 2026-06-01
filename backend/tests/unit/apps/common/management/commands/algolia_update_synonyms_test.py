"""Test cases for the algolia_update_synonyms command."""

from io import StringIO
from unittest.mock import patch

import pytest
from algoliasearch.http.exceptions import AlgoliaException
from django.core.management import call_command


class TestUpdateSynonymsCommand:
    """Test cases for the update_synonyms command."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        """Set up test environment."""
        self.stdout = StringIO()
        with (
            patch("apps.github.index.IssueIndex.update_synonyms") as issue_patch,
            patch("apps.owasp.index.ProjectIndex.update_synonyms") as project_patch,
        ):
            self.mock_issue_update = issue_patch
            self.mock_project_update = project_patch
            yield

    @pytest.mark.parametrize(
        ("issue_count", "project_count", "expected_output"),
        [
            (
                3,
                2,
                "\nThe following models synonyms were reindexed:\n"
                "        * Issues --> 3\n"
                "        * Projects --> 2\n",
            ),
            (
                0,
                0,
                "\nThe following models synonyms were reindexed:\n",
            ),
            (
                3,
                0,
                "\nThe following models synonyms were reindexed:\n        * Issues --> 3\n",
            ),
            (
                0,
                2,
                "\nThe following models synonyms were reindexed:\n        * Projects --> 2\n",
            ),
        ],
    )
    def test_handle_various_updates(self, issue_count, project_count, expected_output):
        """Test command output with different update scenarios."""
        self.mock_issue_update.return_value = issue_count
        self.mock_project_update.return_value = project_count

        with patch("sys.stdout", new=StringIO()) as fake_out:
            call_command("algolia_update_synonyms")
            assert fake_out.getvalue() == expected_output

    def test_handle_exception(self):
        """Test handling of exceptions during update."""
        error_message = "API Error"
        self.mock_issue_update.side_effect = AlgoliaException(error_message)

        with pytest.raises(AlgoliaException) as exc_info:
            call_command("algolia_update_synonyms")

        assert str(exc_info.value) == error_message
        self.mock_issue_update.assert_called_once()
        self.mock_project_update.assert_not_called()

    def test_handle_mixed_results(self):
        """Test when one index returns None and other returns count."""
        self.mock_issue_update.return_value = None
        self.mock_project_update.return_value = 5

        with patch("sys.stdout", new=StringIO()) as fake_out:
            call_command("algolia_update_synonyms")
            assert fake_out.getvalue() == (
                "\nThe following models synonyms were reindexed:\n        * Projects --> 5\n"
            )
