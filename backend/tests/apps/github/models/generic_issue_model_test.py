"""Tests for GenericIssueModel."""

from unittest.mock import Mock

from apps.github.models.generic_issue_model import GenericIssueModel


class TestGenericIssueModel:
    """Test GenericIssueModel class."""

    def test_repository_id_property(self):
        """Test repository_id property returns repository's ID."""
        mock_repository = Mock()
        mock_repository.id = 12345

        # Create a test instance that inherits from GenericIssueModel
        class TestModel(GenericIssueModel):
            class Meta:
                app_label = "github"

        test_instance = TestModel()
        test_instance.repository = mock_repository

        assert test_instance.repository_id == 12345
