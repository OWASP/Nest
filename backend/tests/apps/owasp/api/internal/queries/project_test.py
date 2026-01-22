from unittest.mock import Mock, patch

import pytest

from apps.owasp.api.internal.nodes.project import ProjectNode
from apps.owasp.api.internal.queries.project import ProjectQuery
from apps.owasp.models.project import Project


class TestProjectQuery:
    """Test cases for ProjectQuery class."""

    def test_project_query_has_strawberry_definition(self):
        """Check if ProjectQuery has valid Strawberry definition."""
        assert hasattr(ProjectQuery, "__strawberry_definition__")

        field_names = [field.name for field in ProjectQuery.__strawberry_definition__.fields]
        assert "project" in field_names

    def test_project_field_configuration(self):
        """Test if 'project' field is configured properly."""
        project_field = next(
            field
            for field in ProjectQuery.__strawberry_definition__.fields
            if field.name == "project"
        )

        assert project_field.type.of_type is ProjectNode

        arg_names = [arg.python_name for arg in project_field.arguments]
        assert "key" in arg_names

        key_arg = next(arg for arg in project_field.arguments if arg.python_name == "key")
        assert key_arg.type_annotation.annotation is str


class TestProjectResolution:
    """Test cases for resolving the project field."""

    @pytest.fixture
    def mock_info(self):
        return Mock()

    @pytest.fixture
    def mock_project(self):
        return Mock(spec=Project)

    def test_resolve_project_existing(self, mock_project, mock_info):
        """Test resolving an existing project."""
        with patch("apps.owasp.models.project.Project.objects.get") as mock_only:
            mock_qs = Mock()
            mock_qs.get.return_value = mock_project
            mock_only.return_value = mock_qs

            query = ProjectQuery()
            result = query.__class__.__dict__["project"](query, key="test-project")

            assert result == mock_project
            mock_qs.get.assert_called_once_with(key="www-project-test-project")

    def test_resolve_project_not_found(self, mock_info):
        """Test resolving a non-existent project."""
        with patch("apps.owasp.models.project.Project.objects.get") as mock_only:
            mock_qs = Mock()
            mock_qs.get.side_effect = Project.DoesNotExist
            mock_only.return_value = mock_qs

            query = ProjectQuery()
            result = query.__class__.__dict__["project"](query, key="non-existent")

            assert result is None
            mock_qs.get.assert_called_once_with(key="www-project-non-existent")
