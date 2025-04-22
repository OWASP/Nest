"""Test cases for ProjectQuery."""

from unittest.mock import Mock, patch

import pytest
from graphene import Field, NonNull, String

from apps.common.graphql.queries import BaseQuery
from apps.owasp.graphql.nodes.project import ProjectNode
from apps.owasp.graphql.queries.project import ProjectQuery
from apps.owasp.models.project import Project


class TestProjectQuery:
    """Test cases for ProjectQuery class."""

    def test_project_query_inheritance(self):
        """Test if ProjectQuery inherits from BaseQuery."""
        assert issubclass(ProjectQuery, BaseQuery)

    def test_project_field_configuration(self):
        """Test if project field is properly configured."""
        project_field = ProjectQuery._meta.fields.get("project")
        assert isinstance(project_field, Field)
        assert project_field.type == ProjectNode

        assert "key" in project_field.args
        key_arg = project_field.args["key"]
        assert isinstance(key_arg.type, NonNull)
        assert key_arg.type.of_type == String

    class TestProjectResolution:
        """Test cases for project resolution."""

        @pytest.fixture
        def mock_project(self):
            """Project mock fixture."""
            return Mock(spec=Project)

        @pytest.fixture
        def mock_info(self):
            """GraphQL info mock fixture."""
            return Mock()

        def test_resolve_project_existing(self, mock_project, mock_info):
            """Test resolving an existing project."""
            with patch("apps.owasp.models.project.Project.objects.get") as mock_get:
                mock_get.return_value = mock_project

                result = ProjectQuery.resolve_project(None, mock_info, key="test-project")

                assert result == mock_project
                mock_get.assert_called_once_with(key="www-project-test-project")

        def test_resolve_project_not_found(self, mock_info):
            """Test resolving a non-existent project."""
            with patch("apps.owasp.models.project.Project.objects.get") as mock_get:
                mock_get.side_effect = Project.DoesNotExist

                result = ProjectQuery.resolve_project(None, mock_info, key="non-existent")

                assert result is None
                mock_get.assert_called_once_with(key="www-project-non-existent")
