"""Test cases for ProjectNode."""

from unittest.mock import MagicMock, Mock

import pytest
from graphene import Field, List, String

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.issue import IssueNode
from apps.github.graphql.nodes.release import ReleaseNode
from apps.owasp.graphql.nodes.project import (
    RECENT_ISSUES_LIMIT,
    RECENT_RELEASES_LIMIT,
    ProjectNode,
)
from apps.owasp.models.project import Project


class TestProjectNode:
    """Test cases for ProjectNode class."""

    @pytest.fixture()
    def mock_project(self):
        """Create a mock project with issues and releases."""
        project = Mock(spec=Project)
        mock_issues = MagicMock()
        mock_releases = MagicMock()

        mock_ordered_issues = MagicMock()
        mock_ordered_issues.__getitem__.return_value = []
        mock_issues.select_related.return_value.order_by.return_value = mock_ordered_issues

        mock_ordered_releases = MagicMock()
        mock_ordered_releases.__getitem__.return_value = []
        mock_releases.order_by.return_value = mock_ordered_releases

        project.issues = mock_issues
        project.published_releases = mock_releases
        project.nest_url = "http://example.com/project"
        return project

    def test_project_node_inheritance(self):
        """Test if ProjectNode inherits from BaseNode."""
        assert issubclass(ProjectNode, BaseNode)

    def test_model_meta_configuration(self):
        """Test if model Meta is properly configured."""
        assert ProjectNode._meta.model == Project
        assert len(ProjectNode._meta.fields) > 0

    def test_recent_issues_field(self):
        """Test if recent_issues field is properly configured."""
        recent_issues_field = ProjectNode._meta.fields.get("recent_issues")
        assert isinstance(recent_issues_field, Field)
        assert recent_issues_field.type == List(IssueNode)

    def test_recent_releases_field(self):
        """Test if recent_releases field is properly configured."""
        recent_releases_field = ProjectNode._meta.fields.get("recent_releases")
        assert isinstance(recent_releases_field, Field)
        assert recent_releases_field.type == List(ReleaseNode)

    def test_nest_url_field(self):
        """Test if nest_url field is properly configured."""
        nest_url_field = ProjectNode._meta.fields.get("nest_url")
        assert isinstance(nest_url_field, Field)
        assert nest_url_field.type == String

    def test_resolve_recent_issues(self, mock_project):
        """Test resolution of recent issues."""
        node = ProjectNode()
        node.issues = mock_project.issues

        result = node.resolve_recent_issues(None)

        mock_project.issues.select_related.assert_called_once_with("author")
        mock_project.issues.select_related.return_value.order_by.assert_called_once_with(
            "-created_at"
        )
        mock_project.issues.select_related.return_value.order_by.return_value.__getitem__.assert_called_once_with(
            slice(None, RECENT_ISSUES_LIMIT)
        )
        assert result == []

    def test_resolve_recent_releases(self, mock_project):
        """Test resolution of recent releases."""
        node = ProjectNode()
        node.published_releases = mock_project.published_releases

        result = node.resolve_recent_releases(None)

        mock_project.published_releases.order_by.assert_called_once_with("-published_at")
        mock_project.published_releases.order_by.return_value.__getitem__.assert_called_once_with(
            slice(None, RECENT_RELEASES_LIMIT)
        )
        assert result == []

    def test_resolve_nest_url(self, mock_project):
        """Test resolution of nest_url."""
        node = ProjectNode()
        node.nest_url = mock_project.nest_url

        result = node.resolve_nest_url(None)

        assert result == mock_project.nest_url

    def test_all_fields_exist_in_model(self):
        """Test that all fields in Meta.fields exist in the Project model."""
        model_fields = {f.name for f in Project._meta.get_fields()}
        node_fields = set(ProjectNode._meta.fields.keys())

        custom_fields = {"recent_issues", "recent_releases", "nest_url"}
        node_fields = node_fields - custom_fields

        assert all(field in model_fields for field in node_fields)
