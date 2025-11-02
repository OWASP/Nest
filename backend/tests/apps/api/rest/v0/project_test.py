from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from apps.api.rest.v0.project import ProjectDetail, get_project, list_projects


@pytest.mark.parametrize(
    "project_data",
    [
        {
            "created_at": "2023-01-01T00:00:00Z",
            "description": "A test project by owasp",
            "key": "another-project",
            "level": "other",
            "name": "another project",
            "updated_at": "2023-01-02T00:00:00Z",
        },
        {
            "created_at": "2023-01-01T00:00:00Z",
            "description": "this is not a project, this is just a file",
            "key": "this-is-a-project",
            "level": "incubator",
            "name": "this is a project",
            "updated_at": "2023-01-02T00:00:00Z",
        },
    ],
)
def test_project_serializer_validation(project_data):
    class MockProject:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)
            self.nest_key = data["key"]

    project = ProjectDetail.from_orm(MockProject(project_data))

    assert project.created_at == datetime.fromisoformat(project_data["created_at"])
    assert project.description == project_data["description"]
    assert project.key == project_data["key"]
    assert project.level == project_data["level"]
    assert project.name == project_data["name"]
    assert project.updated_at == datetime.fromisoformat(project_data["updated_at"])


class TestListProjects:
    """Test cases for list_projects endpoint."""

    @patch("apps.api.rest.v0.project.ProjectModel.active_projects")
    def test_list_projects_with_custom_ordering(self, mock_active_projects):
        """Test listing projects with custom ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_ordered = MagicMock()
        mock_final = MagicMock()

        mock_active_projects.order_by.return_value = mock_ordered
        mock_filters.filter.return_value = mock_final

        result = list_projects(mock_request, filters=mock_filters, ordering="created_at")

        mock_active_projects.order_by.assert_called_once_with(
            "created_at", "-stars_count", "-forks_count"
        )
        mock_filters.filter.assert_called_once_with(mock_ordered)
        assert result == mock_final

    @patch("apps.api.rest.v0.project.ProjectModel.active_projects")
    def test_list_projects_with_default_ordering(self, mock_active_projects):
        """Test listing projects with default ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_ordered = MagicMock()
        mock_final = MagicMock()

        mock_active_projects.order_by.return_value = mock_ordered
        mock_filters.filter.return_value = mock_final

        result = list_projects(mock_request, filters=mock_filters, ordering=None)

        mock_active_projects.order_by.assert_called_once_with(
            "-level_raw", "-stars_count", "-forks_count"
        )
        mock_filters.filter.assert_called_once_with(mock_ordered)
        assert result == mock_final


class TestGetProject:
    """Test cases for get_project endpoint."""

    @patch("apps.api.rest.v0.project.ProjectModel.active_projects")
    def test_get_project_without_prefix(self, mock_active_projects):
        """Test getting a project without 'www-project-' prefix (should add it)."""
        mock_request = MagicMock()
        mock_filter = MagicMock()
        mock_project = MagicMock()

        mock_active_projects.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_project

        result = get_project(mock_request, project_id="Nest")

        mock_active_projects.filter.assert_called_once_with(key__iexact="www-project-Nest")
        mock_filter.first.assert_called_once()
        assert result == mock_project

    @patch("apps.api.rest.v0.project.ProjectModel.active_projects")
    def test_get_project_with_prefix(self, mock_active_projects):
        """Test getting a project that already has 'www-project-' prefix."""
        mock_request = MagicMock()
        mock_filter = MagicMock()
        mock_project = MagicMock()

        mock_active_projects.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_project

        result = get_project(mock_request, project_id="www-project-Nest")

        mock_active_projects.filter.assert_called_once_with(key__iexact="www-project-Nest")
        mock_filter.first.assert_called_once()
        assert result == mock_project

    @patch("apps.api.rest.v0.project.ProjectModel.active_projects")
    def test_get_project_uppercase_prefix(self, mock_active_projects):
        """Test getting a project with uppercase prefix (case-insensitive detection)."""
        mock_request = MagicMock()
        mock_filter = MagicMock()
        mock_project = MagicMock()

        mock_active_projects.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_project

        result = get_project(mock_request, project_id="WWW-PROJECT-Nest")

        mock_active_projects.filter.assert_called_once_with(key__iexact="WWW-PROJECT-Nest")
        mock_filter.first.assert_called_once()
        assert result == mock_project

    @patch("apps.api.rest.v0.project.ProjectModel.active_projects")
    def test_get_project_not_found(self, mock_active_projects):
        """Test getting a project that does not exist returns 404."""
        mock_request = MagicMock()
        mock_filter = MagicMock()

        mock_active_projects.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        result = get_project(mock_request, project_id="NonExistent")

        mock_active_projects.filter.assert_called_once_with(key__iexact="www-project-NonExistent")
        mock_filter.first.assert_called_once()
        assert result.status_code == HTTPStatus.NOT_FOUND
        assert b"Project not found" in result.content
