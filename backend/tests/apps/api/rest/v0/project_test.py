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
    class MockMember:
        def __init__(self, login):
            self.login = login

    class MockEntityMember:
        def __init__(self, name, login=None):
            self.member = MockMember(login) if login else None
            self.member_name = name

    class MockProject:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)
            self.nest_key = data["key"]
            self.entity_leaders = [
                MockEntityMember("Alice", "alice"),
                MockEntityMember("Bob"),
            ]

    project = ProjectDetail.from_orm(MockProject(project_data))

    assert project.created_at == datetime.fromisoformat(project_data["created_at"])
    assert project.description == project_data["description"]
    assert project.key == project_data["key"]
    assert len(project.leaders) == 2
    assert project.leaders[0].key == "alice"
    assert project.leaders[0].name == "Alice"
    assert project.leaders[1].key is None
    assert project.leaders[1].name == "Bob"
    assert project.level == project_data["level"]
    assert project.name == project_data["name"]
    assert project.updated_at == datetime.fromisoformat(project_data["updated_at"])


class TestListProjects:
    """Tests for list_projects endpoint."""

    @patch("apps.api.rest.v0.project.apply_structured_search")
    @patch("apps.api.rest.v0.project.ProjectModel")
    def test_list_projects_without_level_filter(self, mock_project_model, mock_apply_search):
        """Test list projects without level filter."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.level = None
        mock_filters.q = None

        mock_queryset = MagicMock()
        mock_apply_search.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset

        result = list_projects(mock_request, mock_filters, ordering=None)

        mock_queryset.order_by.assert_called_with("-level_raw", "-stars_count", "-forks_count")
        assert result == mock_queryset

    @patch("apps.api.rest.v0.project.apply_structured_search")
    @patch("apps.api.rest.v0.project.ProjectModel")
    def test_list_projects_with_level_filter(self, mock_project_model, mock_apply_search):
        """Test list projects with level filter."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.level = "flagship"
        mock_filters.q = "name:security"

        mock_queryset = MagicMock()
        mock_filtered_queryset = MagicMock()
        mock_apply_search.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_filtered_queryset
        mock_filtered_queryset.order_by.return_value = mock_filtered_queryset

        result = list_projects(mock_request, mock_filters, ordering="created_at")

        mock_queryset.filter.assert_called_with(level="flagship")
        mock_filtered_queryset.order_by.assert_called_with(
            "created_at", "-stars_count", "-forks_count"
        )
        assert result == mock_filtered_queryset


class TestGetProject:
    """Tests for get_project endpoint."""

    @patch("apps.api.rest.v0.project.ProjectModel")
    def test_get_project_success(self, mock_project_model):
        """Test get project when found."""
        mock_request = MagicMock()
        mock_project = MagicMock()
        mock_project_model.active_projects.filter.return_value.first.return_value = mock_project

        result = get_project(mock_request, "Nest")

        mock_project_model.active_projects.filter.assert_called_with(
            key__iexact="www-project-Nest"
        )
        assert result == mock_project

    @patch("apps.api.rest.v0.project.ProjectModel")
    def test_get_project_with_prefix(self, mock_project_model):
        """Test get project with www-project- prefix."""
        mock_request = MagicMock()
        mock_project = MagicMock()
        mock_project_model.active_projects.filter.return_value.first.return_value = mock_project

        result = get_project(mock_request, "www-project-Nest")

        mock_project_model.active_projects.filter.assert_called_with(
            key__iexact="www-project-Nest"
        )
        assert result == mock_project

    @patch("apps.api.rest.v0.project.ProjectModel")
    def test_get_project_not_found(self, mock_project_model):
        """Test get project when not found."""
        mock_request = MagicMock()
        mock_project_model.active_projects.filter.return_value.first.return_value = None

        result = get_project(mock_request, "NonExistent")

        assert result.status_code == HTTPStatus.NOT_FOUND
