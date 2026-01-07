"""Test cases for MilestoneNode."""

import math
from unittest.mock import Mock

from apps.github.api.internal.nodes.milestone import MilestoneNode


class TestMilestoneNode:
    """Test cases for MilestoneNode class."""

    def _get_field_by_name(self, name):
        return next(
            (f for f in MilestoneNode.__strawberry_definition__.fields if f.name == name), None
        )

    def test_milestone_node_type(self):
        assert hasattr(MilestoneNode, "__strawberry_definition__")

    def test_milestone_node_fields(self):
        field_names = {field.name for field in MilestoneNode.__strawberry_definition__.fields}
        expected_field_names = {
            "_id",
            "author",
            "body",
            "closed_issues_count",
            "created_at",
            "open_issues_count",
            "organization_name",
            "progress",
            "repository_name",
            "state",
            "title",
            "url",
        }
        assert field_names == expected_field_names

    def test_author_field(self):
        """Test author field resolution."""
        mock_milestone = Mock()
        mock_author = Mock()
        mock_milestone.author = mock_author

        field = self._get_field_by_name("author")
        resolver = field.base_resolver.wrapped_func
        result = resolver(mock_milestone)
        assert result == mock_author

    def test_organization_name_with_organization(self):
        """Test organization_name field when organization exists."""
        mock_milestone = Mock()
        mock_repository = Mock()
        mock_organization = Mock()
        mock_organization.login = "test-org"
        mock_repository.organization = mock_organization
        mock_milestone.repository = mock_repository

        result = MilestoneNode.organization_name(mock_milestone)
        assert result == "test-org"

    def test_organization_name_without_organization(self):
        """Test organization_name field when organization doesn't exist."""
        mock_milestone = Mock()
        mock_repository = Mock()
        mock_repository.organization = None
        mock_milestone.repository = mock_repository

        result = MilestoneNode.organization_name(mock_milestone)
        assert result is None

    def test_organization_name_without_repository(self):
        """Test organization_name field when repository doesn't exist."""
        mock_milestone = Mock()
        mock_milestone.repository = None

        result = MilestoneNode.organization_name(mock_milestone)
        assert result is None

    def test_progress_with_issues(self):
        """Test progress calculation with issues."""
        mock_milestone = Mock()
        mock_milestone.closed_issues_count = 7
        mock_milestone.open_issues_count = 3

        result = MilestoneNode.progress(mock_milestone)
        assert math.isclose(result, 70.0)

    def test_progress_without_issues(self):
        """Test progress calculation without issues."""
        mock_milestone = Mock()
        mock_milestone.closed_issues_count = 0
        mock_milestone.open_issues_count = 0

        result = MilestoneNode.progress(mock_milestone)
        assert math.isclose(result, 0.0)

    def test_repository_name_with_repository(self):
        """Test repository_name field when repository exists."""
        mock_milestone = Mock()
        mock_repository = Mock()
        mock_repository.name = "test-repo"
        mock_milestone.repository = mock_repository

        result = MilestoneNode.repository_name(mock_milestone)
        assert result == "test-repo"

    def test_repository_name_without_repository(self):
        """Test repository_name field when repository doesn't exist."""
        mock_milestone = Mock()
        mock_milestone.repository = None

        result = MilestoneNode.repository_name(mock_milestone)
        assert result is None
