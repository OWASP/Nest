"""Test cases for the algolia_update_replicas command."""

from io import StringIO
from unittest.mock import patch

import pytest
from algoliasearch.http.exceptions import AlgoliaException
from django.core.management import call_command


class TestUpdateReplicasCommand:
    """Test cases for the algolia_update_replicas command."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        """Set up test environment."""
        self.stdout = StringIO()
        with patch("apps.owasp.index.ProjectIndex.configure_replicas") as replica_patch:
            self.mock_replica_update = replica_patch
            yield

    def test_successful_replica_configuration(self):
        """Test successful replica configuration."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            call_command("algolia_update_replicas")

            expected_output = (
                "\n Starting replica configuration...\n"
                "\n Replica have been Successfully created.\n"
            )
            assert fake_out.getvalue() == expected_output
            self.mock_replica_update.assert_called_once()

    def test_handle_exception(self):
        """Test handling of exceptions during replica configuration."""
        error_message = "Failed to configure replicas"
        self.mock_replica_update.side_effect = AlgoliaException(error_message)

        with pytest.raises(AlgoliaException) as exc_info:
            call_command("algolia_update_replicas")

        assert str(exc_info.value) == error_message
        self.mock_replica_update.assert_called_once()
