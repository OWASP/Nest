from unittest.mock import MagicMock, Mock, patch

import pytest
import strawberry

from apps.github.models.user import User as GithubUser
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
        with patch("apps.owasp.models.project.Project.objects.get") as mock_get:
            mock_get.return_value = mock_project

            query = ProjectQuery()
            result = query.__class__.__dict__["project"](query, key="test-project")

            assert result == mock_project
            mock_get.assert_called_once_with(key="www-project-test-project")

    def test_resolve_project_not_found(self, mock_info):
        """Test resolving a non-existent project."""
        with patch("apps.owasp.models.project.Project.objects.get") as mock_get:
            mock_get.side_effect = Project.DoesNotExist

            query = ProjectQuery()
            result = query.__class__.__dict__["project"](query, key="non-existent")

            assert result is None
            mock_get.assert_called_once_with(key="www-project-non-existent")


class TestRecentProjectsResolution:
    """Test cases for resolving recent_projects field."""

    def test_recent_projects_with_positive_limit(self):
        """Test recent_projects returns list within limit."""
        mock_projects = [Mock(spec=Project), Mock(spec=Project)]

        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_filter.return_value.order_by.return_value.__getitem__ = Mock(
                return_value=mock_projects
            )

            query = ProjectQuery()
            result = query.__class__.__dict__["recent_projects"](query, limit=5)

            assert result == mock_projects

    def test_recent_projects_limit_zero_returns_empty(self):
        """Test recent_projects returns empty list when limit is 0."""
        query = ProjectQuery()
        result = query.__class__.__dict__["recent_projects"](query, limit=0)

        assert result == []

    def test_recent_projects_negative_limit_returns_empty(self):
        """Test recent_projects returns empty list when limit is negative."""
        query = ProjectQuery()
        result = query.__class__.__dict__["recent_projects"](query, limit=-5)

        assert result == []


class TestSearchProjectsResolution:
    """Test cases for resolving search_projects field."""

    def test_search_projects_with_valid_query(self):
        """Test search_projects returns a queryset for a valid query."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_queryset = MagicMock()
            mock_queryset.filter.return_value = mock_queryset  # filter returns itself for chaining
            mock_filter.return_value = mock_queryset

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects"](query, query="test")

            # Returns the queryset directly so strawberry-django can apply ordering/pagination
            assert result == mock_queryset.order_by.return_value

    def test_search_projects_single_char_query_returns_results(self):
        """Test search_projects returns results for 1-character queries.

        MIN_SEARCH_QUERY_LENGTH is now 1.
        """
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_queryset = MagicMock()
            mock_queryset.filter.return_value = mock_queryset
            mock_filter.return_value = mock_queryset

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects"](query, query="a")

            assert result == mock_queryset.order_by.return_value
            mock_queryset.filter.assert_called_once_with(name__icontains="a")

    def test_search_projects_two_char_query_returns_results(self):
        """Test search_projects returns results for 2-character queries (previously blocked)."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_queryset = MagicMock()
            mock_queryset.filter.return_value = mock_queryset
            mock_filter.return_value = mock_queryset

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects"](query, query="ab")

            assert result != []

    def test_search_projects_query_too_long(self):
        """Test search_projects returns empty for query > MAX_SEARCH_QUERY_LENGTH."""
        query = ProjectQuery()
        long_query = "a" * 101
        result = query.__class__.__dict__["search_projects"](query, query=long_query)

        assert result == []

    def test_search_projects_whitespace_only_shows_all_projects(self):
        """Test search_projects treats whitespace-only input as empty query."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_queryset = MagicMock()
            mock_filter.return_value = mock_queryset

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects"](query, query="   ")

            mock_queryset.filter.assert_not_called()
            assert result == mock_queryset.order_by.return_value


class TestIsProjectLeaderResolution:
    """Test cases for resolving is_project_leader field."""

    @pytest.fixture
    def mock_info(self):
        return Mock()

    def test_is_project_leader_user_not_found(self, mock_info):
        """Test is_project_leader returns False when user doesn't exist."""
        with patch("apps.owasp.api.internal.queries.project.GithubUser.objects.get") as mock_get:
            mock_get.side_effect = GithubUser.DoesNotExist

            query = ProjectQuery()
            result = query.__class__.__dict__["is_project_leader"](
                query, info=mock_info, login="nonexistent"
            )

            assert not result

    def test_is_project_leader_user_is_leader(self, mock_info):
        """Test is_project_leader returns True when user is a leader."""
        mock_user = Mock()
        mock_user.login = "testuser"
        mock_user.name = "Test User"

        with (
            patch(
                "apps.owasp.api.internal.queries.project.GithubUser.objects.get"
            ) as mock_get_user,
            patch("apps.owasp.models.project.Project.objects.filter") as mock_filter,
        ):
            mock_get_user.return_value = mock_user
            mock_filter.return_value.exists.return_value = True

            query = ProjectQuery()
            result = query.__class__.__dict__["is_project_leader"](
                query, info=mock_info, login="testuser"
            )

            assert result

    def test_is_project_leader_user_not_leader(self, mock_info):
        """Test is_project_leader returns False when user is not a leader."""
        mock_user = Mock()
        mock_user.login = "testuser"
        mock_user.name = "Test User"

        with (
            patch(
                "apps.owasp.api.internal.queries.project.GithubUser.objects.get"
            ) as mock_get_user,
            patch("apps.owasp.models.project.Project.objects.filter") as mock_filter,
        ):
            mock_get_user.return_value = mock_user
            mock_filter.return_value.exists.return_value = False

            query = ProjectQuery()
            result = query.__class__.__dict__["is_project_leader"](
                query, info=mock_info, login="testuser"
            )

            assert not result


class TestProjectsResolution:
    """Test cases for resolving projects field with pagination."""

    def test_projects_without_ordering(self):
        """Test projects applies default ordering when no ordering specified."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_queryset = MagicMock()
            mock_filter.return_value = mock_queryset

            query = ProjectQuery()
            query.__class__.__dict__["projects"](query)

            mock_queryset.order_by.assert_called_with("-stars_count", "-created_at")

    def test_projects_with_ordering(self):
        """Test projects does not apply default ordering when ordering provided."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_queryset = MagicMock()
            mock_filter.return_value = mock_queryset

            query = ProjectQuery()
            query.__class__.__dict__["projects"](query, ordering=[Mock()])

            mock_queryset.order_by.assert_not_called()

    def test_projects_with_negative_pagination_offset(self):
        """Test projects returns empty list for negative offset."""
        pagination = MagicMock()
        pagination.offset = -1

        query = ProjectQuery()
        result = query.__class__.__dict__["projects"](query, pagination=pagination)

        assert result == []

    def test_projects_with_zero_pagination_limit(self):
        """Test projects returns empty list for zero limit."""
        pagination = MagicMock()
        pagination.offset = 0
        pagination.limit = 0

        query = ProjectQuery()
        result = query.__class__.__dict__["projects"](query, pagination=pagination)

        assert result == []

    def test_projects_with_negative_pagination_limit(self):
        """Test projects returns empty list for negative limit."""
        pagination = MagicMock()
        pagination.offset = 0
        pagination.limit = -5

        query = ProjectQuery()
        result = query.__class__.__dict__["projects"](query, pagination=pagination)

        assert result == []

    def test_projects_with_valid_pagination(self):
        """Test projects with valid pagination parameters."""
        pagination = MagicMock()
        pagination.offset = 10
        pagination.limit = 50

        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_queryset = MagicMock()
            mock_filter.return_value = mock_queryset

            query = ProjectQuery()
            query.__class__.__dict__["projects"](query, pagination=pagination)

            assert pagination.offset == 10
            assert pagination.limit == 50

    def test_projects_pagination_offset_capped_to_max(self):
        """Test projects caps offset to MAX_OFFSET."""
        pagination = MagicMock()
        pagination.offset = 20000
        pagination.limit = None

        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_filter.return_value = MagicMock()

            query = ProjectQuery()
            query.__class__.__dict__["projects"](query, pagination=pagination)

            assert pagination.offset == 10000  # MAX_OFFSET

    def test_projects_pagination_limit_capped_to_max(self):
        """Test projects caps limit to MAX_PROJECTS_LIMIT."""
        pagination = MagicMock()
        pagination.offset = 0
        pagination.limit = 5000

        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_filter.return_value = MagicMock()

            query = ProjectQuery()
            query.__class__.__dict__["projects"](query, pagination=pagination)

            assert pagination.limit == 1000

    def test_projects_pagination_limit_unset(self):
        """Test projects handles UNSET limit gracefully."""
        pagination = MagicMock()
        pagination.offset = 0
        pagination.limit = strawberry.UNSET

        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_queryset = MagicMock()
            mock_queryset.order_by.return_value = mock_queryset
            mock_filter.return_value = mock_queryset

            query = ProjectQuery()
            result = query.__class__.__dict__["projects"](query, pagination=pagination)

            assert result == mock_queryset


class TestSearchProjectsPagination:
    """Test cases for search_projects pagination scenarios."""

    def test_search_projects_with_negative_pagination_offset(self):
        """Test search_projects returns empty list for negative offset."""
        pagination = MagicMock()
        pagination.offset = -1

        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_filter.return_value = MagicMock()

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects"](
                query, query="test", pagination=pagination
            )

            assert result == []

    def test_search_projects_with_zero_pagination_limit(self):
        """Test search_projects returns empty list for zero limit."""
        pagination = MagicMock()
        pagination.offset = 0
        pagination.limit = 0

        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_filter.return_value = MagicMock()

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects"](
                query, query="test", pagination=pagination
            )

            assert result == []

    def test_search_projects_with_negative_pagination_limit(self):
        """Test search_projects returns empty list for negative limit."""
        pagination = MagicMock()
        pagination.offset = 0
        pagination.limit = -5

        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_filter.return_value = MagicMock()

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects"](
                query, query="test", pagination=pagination
            )

            assert result == []

    def test_search_projects_pagination_offset_capped_to_max(self):
        """Test search_projects caps offset to MAX_OFFSET."""
        pagination = MagicMock()
        pagination.offset = 20000
        pagination.limit = None

        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_queryset = MagicMock()
            mock_filter.return_value = mock_queryset

            query = ProjectQuery()
            query.__class__.__dict__["search_projects"](query, query="test", pagination=pagination)

            assert pagination.offset == 10000  # MAX_OFFSET

    def test_search_projects_pagination_limit_capped_to_max(self):
        """Test search_projects caps limit to MAX_PROJECTS_LIMIT."""
        pagination = MagicMock()
        pagination.offset = 0
        pagination.limit = 5000

        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_queryset = MagicMock()
            mock_filter.return_value = mock_queryset

            query = ProjectQuery()
            query.__class__.__dict__["search_projects"](query, query="test", pagination=pagination)

            assert pagination.limit == 1000

    def test_search_projects_pagination_limit_unset(self):
        """Test search_projects handles UNSET limit gracefully."""
        pagination = MagicMock()
        pagination.offset = 0
        pagination.limit = strawberry.UNSET

        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_queryset = MagicMock()
            mock_queryset.filter.return_value = mock_queryset
            mock_filter.return_value = mock_queryset

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects"](
                query, query="test", pagination=pagination
            )

            # The raw queryset (after name filter + default ordering) is returned
            assert result == mock_queryset.filter.return_value.order_by.return_value

    def test_search_projects_with_ordering(self):
        """Test search_projects does not apply default ordering when ordering provided."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_queryset = MagicMock()
            mock_queryset.filter.return_value = mock_queryset
            mock_filter.return_value = mock_queryset

            query = ProjectQuery()
            query.__class__.__dict__["search_projects"](query, query="test", ordering=[Mock()])

            mock_queryset.order_by.assert_not_called()

    def test_search_projects_empty_query_shows_all(self):
        """Test search_projects with empty query returns queryset of all projects."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_queryset = MagicMock()
            mock_filter.return_value = mock_queryset

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects"](query, query="")

            # Should not filter by name when query is empty
            mock_queryset.filter.assert_not_called()
            # Returns the queryset (after default ordering) for strawberry-django to paginate
            assert result == mock_queryset.order_by.return_value


class TestSearchProjectsCountResolution:
    """Test cases for resolving search_projects_count field."""

    def test_search_projects_count_with_empty_query(self):
        """Test search_projects_count with empty query returns total count."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_queryset = MagicMock()
            mock_queryset.count.return_value = 100
            mock_filter.return_value = mock_queryset

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects_count"](query, query="")

            assert result == 100
            mock_queryset.filter.assert_not_called()

    def test_search_projects_count_with_valid_query(self):
        """Test search_projects_count with valid query returns filtered count."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_queryset = MagicMock()
            mock_filtered = MagicMock()
            mock_filtered.count.return_value = 10
            mock_queryset.filter.return_value = mock_filtered
            mock_filter.return_value = mock_queryset

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects_count"](query, query="security")

            assert result == 10
            mock_queryset.filter.assert_called_with(name__icontains="security")

    def test_search_projects_count_with_whitespace_query(self):
        """Test search_projects_count trims whitespace from query."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_queryset = MagicMock()
            mock_filtered = MagicMock()
            mock_filtered.count.return_value = 5
            mock_queryset.filter.return_value = mock_filtered
            mock_filter.return_value = mock_queryset

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects_count"](query, query="  test  ")

            assert result == 5
            mock_queryset.filter.assert_called_with(name__icontains="test")

    def test_search_projects_count_with_long_query_bounded(self):
        """Test search_projects_count returns 0 for query > MAX_SEARCH_QUERY_LENGTH."""
        long_query = "a" * 150

        query = ProjectQuery()
        result = query.__class__.__dict__["search_projects_count"](query, query=long_query)

        assert result == 0

    def test_search_projects_count_with_filters(self):
        """Test search_projects_count applies filters when provided."""
        mock_filters = MagicMock()

        with (
            patch("apps.owasp.models.project.Project.objects.filter") as mock_filter,
            patch(
                "apps.owasp.api.internal.queries.project.strawberry_django.filters.apply"
            ) as mock_apply_filters,
        ):
            mock_queryset = MagicMock()
            mock_queryset.count.return_value = 20
            mock_filter.return_value = mock_queryset
            mock_apply_filters.return_value = mock_queryset

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects_count"](
                query, query="", filters=mock_filters
            )

            assert result == 20
            mock_apply_filters.assert_called_once_with(mock_filters, mock_queryset)
