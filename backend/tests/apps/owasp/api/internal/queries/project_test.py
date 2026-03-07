from unittest.mock import Mock, patch

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
        """Test search_projects returns matching projects."""
        mock_projects = [Mock(spec=Project)]

        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_qs = Mock()
            mock_filter.return_value = mock_qs
            mock_qs.filter.return_value = mock_qs
            mock_qs.order_by.return_value = mock_qs
            mock_qs.__getitem__ = Mock(return_value=mock_projects)

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects"](query, query="test")

            assert result == mock_qs

    def test_search_projects_query_too_short(self):
        """Test search_projects returns empty for empty query after strip."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_qs = Mock()
            mock_filter.return_value = mock_qs
            mock_qs.order_by.return_value = mock_qs

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects"](query, query="")
            assert result == mock_qs

    def test_search_projects_query_too_long(self):
        """Test search_projects returns empty for query > MAX_SEARCH_QUERY_LENGTH."""
        query = ProjectQuery()
        long_query = "a" * 101
        result = query.__class__.__dict__["search_projects"](query, query=long_query)

        assert result == []

    def test_search_projects_whitespace_trimmed(self):
        """Test search_projects trims whitespace before checking length."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_qs = Mock()
            mock_filter.return_value = mock_qs
            mock_qs.order_by.return_value = mock_qs

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects"](query, query="   ")
            assert result == mock_qs


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
    """Test cases for resolving projects field."""

    def test_projects_default_ordering_no_ordering(self):
        """Test projects applies default ordering when no ordering is provided."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_qs = Mock()
            mock_filter.return_value = mock_qs
            mock_qs.order_by.return_value = mock_qs

            query = ProjectQuery()
            result = query.__class__.__dict__["projects"](query)

            mock_qs.order_by.assert_called_once_with("-stars_count", "-created_at")
            assert result == mock_qs

    def test_projects_with_ordering_skips_default(self):
        """Test projects skips default ordering when ordering is provided."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_qs = Mock()
            mock_filter.return_value = mock_qs

            query = ProjectQuery()
            result = query.__class__.__dict__["projects"](query, ordering=[Mock()])

            mock_qs.order_by.assert_not_called()
            assert result == mock_qs

    def test_projects_pagination_negative_offset_returns_empty(self):
        """Test projects returns empty list for negative offset."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_qs = Mock()
            mock_filter.return_value = mock_qs
            mock_qs.order_by.return_value = mock_qs

            pagination = Mock()
            pagination.offset = -1
            pagination.limit = 10

            query = ProjectQuery()
            result = query.__class__.__dict__["projects"](query, pagination=pagination)

            assert result == []

    def test_projects_pagination_offset_clamped_to_max(self):
        """Test projects clamps offset to MAX_OFFSET."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_qs = Mock()
            mock_filter.return_value = mock_qs
            mock_qs.order_by.return_value = mock_qs

            pagination = Mock()
            pagination.offset = 50000
            pagination.limit = None

            query = ProjectQuery()
            query.__class__.__dict__["projects"](query, pagination=pagination)

            assert pagination.offset == 10000

    def test_projects_pagination_zero_limit_returns_empty(self):
        """Test projects returns empty list for zero limit."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_qs = Mock()
            mock_filter.return_value = mock_qs
            mock_qs.order_by.return_value = mock_qs

            pagination = Mock()
            pagination.offset = 0
            pagination.limit = 0

            query = ProjectQuery()
            result = query.__class__.__dict__["projects"](query, pagination=pagination)

            assert result == []

    def test_projects_pagination_negative_limit_returns_empty(self):
        """Test projects returns empty list for negative limit."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_qs = Mock()
            mock_filter.return_value = mock_qs
            mock_qs.order_by.return_value = mock_qs

            pagination = Mock()
            pagination.offset = 0
            pagination.limit = -5

            query = ProjectQuery()
            result = query.__class__.__dict__["projects"](query, pagination=pagination)

            assert result == []

    def test_projects_pagination_limit_clamped_to_max(self):
        """Test projects clamps limit to MAX_PROJECTS_LIMIT."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_qs = Mock()
            mock_filter.return_value = mock_qs
            mock_qs.order_by.return_value = mock_qs

            pagination = Mock()
            pagination.offset = 0
            pagination.limit = 5000

            query = ProjectQuery()
            query.__class__.__dict__["projects"](query, pagination=pagination)

            assert pagination.limit == 1000

    def test_projects_pagination_limit_unset(self):
        """Test projects handles UNSET limit properly."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_qs = Mock()
            mock_filter.return_value = mock_qs
            mock_qs.order_by.return_value = mock_qs

            pagination = Mock()
            pagination.offset = 0
            pagination.limit = strawberry.UNSET

            query = ProjectQuery()
            result = query.__class__.__dict__["projects"](query, pagination=pagination)
            assert result == mock_qs


class TestSearchProjectsPagination:
    """Test cases for search_projects pagination edge cases."""

    def test_search_projects_pagination_negative_offset(self):
        """Test search_projects returns empty for negative offset."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_qs = Mock()
            mock_filter.return_value = mock_qs
            mock_qs.order_by.return_value = mock_qs

            pagination = Mock()
            pagination.offset = -1
            pagination.limit = 10

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects"](
                query, query="test", pagination=pagination
            )

            assert result == []

    def test_search_projects_pagination_offset_clamped(self):
        """Test search_projects clamps offset to MAX_OFFSET."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_qs = Mock()
            mock_filter.return_value = mock_qs
            mock_qs.filter.return_value = mock_qs
            mock_qs.order_by.return_value = mock_qs

            pagination = Mock()
            pagination.offset = 50000
            pagination.limit = None

            query = ProjectQuery()
            query.__class__.__dict__["search_projects"](query, query="test", pagination=pagination)

            assert pagination.offset == 10000

    def test_search_projects_pagination_zero_limit(self):
        """Test search_projects returns empty for zero limit."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_qs = Mock()
            mock_filter.return_value = mock_qs
            mock_qs.filter.return_value = mock_qs
            mock_qs.order_by.return_value = mock_qs

            pagination = Mock()
            pagination.offset = 0
            pagination.limit = 0

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects"](
                query, query="test", pagination=pagination
            )

            assert result == []

    def test_search_projects_pagination_negative_limit(self):
        """Test search_projects returns empty for negative limit."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_qs = Mock()
            mock_filter.return_value = mock_qs
            mock_qs.filter.return_value = mock_qs
            mock_qs.order_by.return_value = mock_qs

            pagination = Mock()
            pagination.offset = 0
            pagination.limit = -5

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects"](
                query, query="test", pagination=pagination
            )

            assert result == []

    def test_search_projects_pagination_limit_clamped(self):
        """Test search_projects clamps limit to MAX_PROJECTS_LIMIT."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_qs = Mock()
            mock_filter.return_value = mock_qs
            mock_qs.filter.return_value = mock_qs
            mock_qs.order_by.return_value = mock_qs

            pagination = Mock()
            pagination.offset = 0
            pagination.limit = 5000

            query = ProjectQuery()
            query.__class__.__dict__["search_projects"](query, query="test", pagination=pagination)

            assert pagination.limit == 1000

    def test_search_projects_pagination_limit_unset(self):
        """Test search_projects handles UNSET limit properly."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_qs = Mock()
            mock_filter.return_value = mock_qs
            mock_qs.filter.return_value = mock_qs
            mock_qs.order_by.return_value = mock_qs

            pagination = Mock()
            pagination.offset = 0
            pagination.limit = strawberry.UNSET

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects"](
                query, query="test", pagination=pagination
            )

            assert result == mock_qs

    def test_search_projects_with_ordering_skips_default(self):
        """Test search_projects skips default ordering when ordering is provided."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_qs = Mock()
            mock_filter.return_value = mock_qs
            mock_qs.filter.return_value = mock_qs

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects"](
                query, query="test", ordering=[Mock()]
            )

            mock_qs.order_by.assert_not_called()
            assert result == mock_qs


class TestSearchProjectsCountResolution:
    """Test cases for resolving search_projects_count field."""

    def test_search_projects_count_empty_query(self):
        """Test search_projects_count returns count for empty query."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_qs = Mock()
            mock_filter.return_value = mock_qs
            mock_qs.count.return_value = 42

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects_count"](query, query="")

            assert result == 42
            mock_qs.count.assert_called_once()

    def test_search_projects_count_with_query(self):
        """Test search_projects_count filters by query."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter:
            mock_qs = Mock()
            mock_filter.return_value = mock_qs
            mock_qs.filter.return_value = mock_qs
            mock_qs.count.return_value = 5

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects_count"](query, query="security")

            assert result == 5
            mock_qs.filter.assert_called_once_with(name__icontains="security")

    def test_search_projects_count_query_too_long(self):
        """Test search_projects_count returns 0 for query > MAX_SEARCH_QUERY_LENGTH."""
        query = ProjectQuery()
        long_query = "a" * 101
        result = query.__class__.__dict__["search_projects_count"](query, query=long_query)

        assert result == 0

    def test_search_projects_count_with_filters(self):
        """Test search_projects_count applies filters."""
        with (
            patch("apps.owasp.models.project.Project.objects.filter") as mock_filter,
            patch(
                "apps.owasp.api.internal.queries.project.strawberry_django.filters.apply"
            ) as mock_apply,
        ):
            mock_qs = Mock()
            mock_filter.return_value = mock_qs
            mock_apply.return_value = mock_qs
            mock_qs.count.return_value = 10

            mock_filters = Mock()
            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects_count"](
                query, query="", filters=mock_filters
            )

            assert result == 10
            mock_apply.assert_called_once_with(mock_filters, mock_qs)

    def test_search_projects_count_with_query_and_filters(self):
        """Test search_projects_count with both query and filters."""
        with (
            patch("apps.owasp.models.project.Project.objects.filter") as mock_filter,
            patch(
                "apps.owasp.api.internal.queries.project.strawberry_django.filters.apply"
            ) as mock_apply,
        ):
            mock_qs = Mock()
            mock_filter.return_value = mock_qs
            mock_qs.filter.return_value = mock_qs
            mock_apply.return_value = mock_qs
            mock_qs.count.return_value = 3

            mock_filters = Mock()
            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects_count"](
                query, query="test", filters=mock_filters
            )

            assert result == 3
            mock_qs.filter.assert_called_once_with(name__icontains="test")
            mock_apply.assert_called_once_with(mock_filters, mock_qs)
