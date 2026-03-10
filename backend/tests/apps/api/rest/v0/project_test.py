"""Tests for project API."""

from datetime import datetime
from http import HTTPStatus
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from django.http import HttpResponse
from pydantic import ValidationError

from apps.api.rest.v0.project import (
    PROJECT_SEARCH_FIELDS,
    ProjectDetail,
    ProjectFilter,
    get_project,
    list_projects,
)
from apps.owasp.models.enums.project import ProjectType


class MockMember:
    """Mock for entity member's login."""

    def __init__(self, login: str | None) -> None:
        self.login = login


class MockEntityMember:
    """Mock for entity leader with optional member login."""

    def __init__(self, name: str, login: str | None = None) -> None:
        self.member = MockMember(login) if login else None
        self.member_name = name


class MockProject:
    """Mock project model for serializer validation."""

    def __init__(self, data: dict[str, Any]) -> None:
        for key, value in data.items():
            setattr(self, key, value)
        self.nest_key = data["key"]
        self.entity_leaders = [
            MockEntityMember("Alice", "alice"),
            MockEntityMember("Bob"),
        ]


class TestProjectSerializerValidation:
    """Tests for ProjectDetail serializer validation."""

    @pytest.mark.parametrize(
        "project_data",
        [
            {
                "created_at": "2023-01-01T00:00:00Z",
                "description": "A test project by owasp",
                "key": "another-project",
                "level": "other",
                "name": "another project",
                "type": "documentation",
                "updated_at": "2023-01-02T00:00:00Z",
            },
            {
                "created_at": "2023-01-01T00:00:00Z",
                "description": "this is not a project, this is just a file",
                "key": "this-is-a-project",
                "level": "incubator",
                "name": "this is a project",
                "type": "code",
                "updated_at": "2023-01-02T00:00:00Z",
            },
        ],
    )
    def test_project_serializer_validation(self, project_data: dict[str, Any]) -> None:
        """Test ProjectDetail serializes mock project correctly."""
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
        assert project.type == project_data["type"]
        assert project.updated_at == datetime.fromisoformat(project_data["updated_at"])


class TestListProjects:
    """Tests for list_projects endpoint."""

    @pytest.fixture
    def mock_request(self) -> MagicMock:
        """Create mock HTTP request."""
        return MagicMock()

    @pytest.fixture
    def mock_queryset(self) -> MagicMock:
        """Create mock queryset that chains filter and order_by."""
        queryset = MagicMock()
        queryset.filter.return_value = queryset
        queryset.order_by.return_value = queryset
        return queryset

    @patch("apps.api.rest.v0.project.apply_structured_search")
    @patch("apps.api.rest.v0.project.ProjectModel")
    def test_list_projects_without_level_filter(
        self,
        mock_project_model: MagicMock,
        mock_apply_search: MagicMock,
        mock_request: MagicMock,
        mock_queryset: MagicMock,
    ) -> None:
        """Test list projects without level filter."""
        mock_filters = MagicMock()
        mock_filters.level = None
        mock_filters.q = None
        mock_filters.type = None

        mock_apply_search.return_value = mock_queryset

        result = list_projects(mock_request, mock_filters, ordering=None)

        mock_apply_search.assert_called_once_with(
            queryset=mock_project_model.active_projects,
            query=None,
            field_schema=PROJECT_SEARCH_FIELDS,
        )
        mock_queryset.order_by.assert_called_once_with(
            "-level_raw", "-stars_count", "-forks_count", "pk"
        )
        assert result == mock_queryset

    @patch("apps.api.rest.v0.project.apply_structured_search")
    @patch("apps.api.rest.v0.project.ProjectModel")
    def test_list_projects_with_level_filter(
        self,
        mock_project_model: MagicMock,
        mock_apply_search: MagicMock,
        mock_request: MagicMock,
        mock_queryset: MagicMock,
    ) -> None:
        """Test list projects with level filter."""
        mock_filters = MagicMock()
        mock_filters.level = "flagship"
        mock_filters.q = "name:security"
        mock_filters.type = None

        mock_filtered_queryset = MagicMock()
        mock_filtered_queryset.order_by.return_value = mock_filtered_queryset
        mock_apply_search.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_filtered_queryset

        result = list_projects(mock_request, mock_filters, ordering="created_at")

        mock_apply_search.assert_called_once_with(
            queryset=mock_project_model.active_projects,
            query="name:security",
            field_schema=PROJECT_SEARCH_FIELDS,
        )
        mock_queryset.filter.assert_called_once_with(level="flagship")
        mock_filtered_queryset.order_by.assert_called_once_with(
            "created_at", "-stars_count", "-forks_count", "pk"
        )
        assert result == mock_filtered_queryset

    @patch("apps.api.rest.v0.project.apply_structured_search")
    @patch("apps.api.rest.v0.project.ProjectModel")
    def test_list_projects_calls_apply_structured_search_with_query(
        self,
        mock_project_model: MagicMock,
        mock_apply_search: MagicMock,
        mock_request: MagicMock,
        mock_queryset: MagicMock,
    ) -> None:
        """Test apply_structured_search receives filters.q correctly."""
        mock_filters = MagicMock()
        mock_filters.level = None
        mock_filters.q = "name:nest stars:>100"
        mock_filters.type = None

        mock_apply_search.return_value = mock_queryset

        list_projects(mock_request, mock_filters, ordering=None)

        mock_apply_search.assert_called_once_with(
            queryset=mock_project_model.active_projects,
            query="name:nest stars:>100",
            field_schema=PROJECT_SEARCH_FIELDS,
        )

    @patch("apps.api.rest.v0.project.apply_structured_search")
    @patch("apps.api.rest.v0.project.ProjectModel")
    def test_list_projects_with_single_type_filter(
        self,
        mock_project_model: MagicMock,
        mock_apply_search: MagicMock,
        mock_request: MagicMock,
        mock_queryset: MagicMock,
    ) -> None:
        """Test list projects filtered by a single type."""
        mock_filters = MagicMock()
        mock_filters.level = None
        mock_filters.type = ["code"]
        mock_filters.q = None

        mock_filtered_queryset = MagicMock()
        mock_filtered_queryset.order_by.return_value = mock_filtered_queryset
        mock_apply_search.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_filtered_queryset

        result = list_projects(mock_request, mock_filters, ordering=None)

        mock_queryset.filter.assert_called_once_with(type__in=["code"])
        mock_filtered_queryset.order_by.assert_called_once_with(
            "-level_raw", "-stars_count", "-forks_count", "pk"
        )
        assert result == mock_filtered_queryset

    @patch("apps.api.rest.v0.project.apply_structured_search")
    @patch("apps.api.rest.v0.project.ProjectModel")
    def test_list_projects_with_multiple_type_filter(
        self,
        mock_project_model: MagicMock,
        mock_apply_search: MagicMock,
        mock_request: MagicMock,
        mock_queryset: MagicMock,
    ) -> None:
        """Test list projects filtered by multiple types."""
        mock_filters = MagicMock()
        mock_filters.level = None
        mock_filters.type = ["code", "tool"]
        mock_filters.q = None

        mock_filtered_queryset = MagicMock()
        mock_filtered_queryset.order_by.return_value = mock_filtered_queryset
        mock_apply_search.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_filtered_queryset

        result = list_projects(mock_request, mock_filters, ordering=None)

        mock_queryset.filter.assert_called_once_with(type__in=["code", "tool"])
        mock_filtered_queryset.order_by.assert_called_once_with(
            "-level_raw", "-stars_count", "-forks_count", "pk"
        )
        assert result == mock_filtered_queryset

    @patch("apps.api.rest.v0.project.apply_structured_search")
    @patch("apps.api.rest.v0.project.ProjectModel")
    def test_list_projects_with_type_and_level_filter(
        self,
        mock_project_model: MagicMock,
        mock_apply_search: MagicMock,
        mock_request: MagicMock,
        mock_queryset: MagicMock,
    ) -> None:
        """Test list projects filtered by both type and level."""
        mock_filters = MagicMock()
        mock_filters.level = "flagship"
        mock_filters.type = ["code"]
        mock_filters.q = None

        mock_level_filtered = MagicMock()
        mock_type_filtered = MagicMock()
        mock_type_filtered.order_by.return_value = mock_type_filtered
        mock_apply_search.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_level_filtered
        mock_level_filtered.filter.return_value = mock_type_filtered

        result = list_projects(mock_request, mock_filters, ordering=None)

        mock_queryset.filter.assert_called_once_with(level="flagship")
        mock_level_filtered.filter.assert_called_once_with(type__in=["code"])
        mock_type_filtered.order_by.assert_called_once_with(
            "-level_raw", "-stars_count", "-forks_count", "pk"
        )
        assert result == mock_type_filtered

    @pytest.mark.parametrize(
        ("ordering", "expected_order"),
        [
            ("created_at", ("created_at", "-stars_count", "-forks_count", "pk")),
            ("-created_at", ("-created_at", "-stars_count", "-forks_count", "pk")),
            ("updated_at", ("updated_at", "-stars_count", "-forks_count", "pk")),
            ("-updated_at", ("-updated_at", "-stars_count", "-forks_count", "pk")),
            ("level", ("level_raw", "-stars_count", "-forks_count", "pk")),
            ("-level", ("-level_raw", "-stars_count", "-forks_count", "pk")),
        ],
    )
    @patch("apps.api.rest.v0.project.apply_structured_search")
    @patch("apps.api.rest.v0.project.ProjectModel")
    def test_list_projects_ordering_variations(
        self,
        mock_project_model: MagicMock,
        mock_apply_search: MagicMock,
        mock_request: MagicMock,
        mock_queryset: MagicMock,
        ordering: str,
        expected_order: tuple[str, ...],
    ) -> None:
        """Test list projects with different ordering options."""
        mock_filters = MagicMock()
        mock_filters.level = None
        mock_filters.q = None
        mock_filters.type = None

        mock_apply_search.return_value = mock_queryset

        list_projects(mock_request, mock_filters, ordering=ordering)

        mock_queryset.order_by.assert_called_once_with(*expected_order)


class TestProjectFilter:
    """Unit tests for ProjectFilter schema validation."""

    def test_filter_rejects_invalid_type(self) -> None:
        """ProjectFilter raises ValidationError for invalid type values."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectFilter.model_validate({"type": ["invalid"]})

        errors = exc_info.value.errors()
        assert errors

    def test_filter_accepts_valid_types(self) -> None:
        """ProjectFilter accepts valid ProjectType enum values."""
        filters = ProjectFilter.model_validate({"type": ["code", "tool"]})
        assert filters.type == [ProjectType.CODE, ProjectType.TOOL]

    def test_filter_accepts_single_valid_type(self) -> None:
        """ProjectFilter accepts a single valid type."""
        filters = ProjectFilter.model_validate({"type": ["documentation"]})
        assert filters.type == [ProjectType.DOCUMENTATION]

    def test_filter_accepts_none_type(self) -> None:
        """ProjectFilter accepts missing or null type."""
        filters = ProjectFilter.model_validate({})
        assert filters.type is None


class TestGetProject:
    """Tests for get_project endpoint."""

    @patch("apps.api.rest.v0.project.ProjectModel")
    def test_get_project_success(self, mock_project_model: MagicMock) -> None:
        """Test get project when found."""
        mock_request = MagicMock()
        mock_project = MagicMock()
        mock_project_model.active_projects.filter.return_value.first.return_value = mock_project

        result = get_project(mock_request, "Nest")

        mock_project_model.active_projects.filter.assert_called_once_with(
            key__iexact="www-project-Nest"
        )
        assert result == mock_project

    @patch("apps.api.rest.v0.project.ProjectModel")
    def test_get_project_with_prefix(self, mock_project_model: MagicMock) -> None:
        """Test get project with www-project- prefix preserves case."""
        mock_request = MagicMock()
        mock_project = MagicMock()
        mock_project_model.active_projects.filter.return_value.first.return_value = mock_project

        result = get_project(mock_request, "www-project-Nest")

        mock_project_model.active_projects.filter.assert_called_once_with(
            key__iexact="www-project-Nest"
        )
        assert result == mock_project

    @patch("apps.api.rest.v0.project.ProjectModel")
    def test_get_project_not_found(self, mock_project_model: MagicMock) -> None:
        """Test get project returns 404 response when not found."""
        mock_request = MagicMock()
        mock_project_model.active_projects.filter.return_value.first.return_value = None

        result = get_project(mock_request, "NonExistent")

        assert isinstance(result, HttpResponse)
        assert result.status_code == HTTPStatus.NOT_FOUND
