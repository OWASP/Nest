"""Test cases for the algolia_update_replicas command."""

from io import StringIO
from unittest.mock import patch

import pytest
from algoliasearch.http.exceptions import AlgoliaException
from django.core.management import call_command
from django.core.management.base import CommandError


class TestUpdateReplicasCommand:
    """Test cases for the algolia_update_replicas command."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        """Set up test environment."""
        self.stdout = StringIO()
        with (
            patch("apps.owasp.index.ChapterIndex.configure_replicas") as chapter_replica_patch,
            patch(
                "apps.mentorship.index.ProgramIndex.configure_replicas"
            ) as program_replica_patch,
            patch("apps.owasp.index.ProjectIndex.configure_replicas") as project_replica_patch,
        ):
            self.mock_chapter_replica_update = chapter_replica_patch
            self.mock_program_replica_update = program_replica_patch
            self.mock_project_replica_update = project_replica_patch
            yield

    def test_successful_replica_configuration(self):
        """Test successful replica configuration."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            call_command("algolia_update_replicas")

            expected_output = (
                "\n Starting replica configuration...\n"
                "\n Replicas have been successfully created.\n"
            )
            assert fake_out.getvalue() == expected_output
            self.mock_chapter_replica_update.assert_called_once()
            self.mock_program_replica_update.assert_called_once()
            self.mock_project_replica_update.assert_called_once()

    def test_failure_does_not_block_other_indices(self):
        """Test that one failing index does not prevent the others from updating."""
        error_message = "Failed to configure replicas"
        self.mock_program_replica_update.side_effect = AlgoliaException(error_message)

        with pytest.raises(CommandError, match="ProgramIndex"):
            call_command("algolia_update_replicas")

        self.mock_chapter_replica_update.assert_called_once()
        self.mock_program_replica_update.assert_called_once()
        self.mock_project_replica_update.assert_called_once()
