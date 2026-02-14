from unittest.mock import Mock, patch

import pytest

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
            mock_filter.return_value.order_by.return_value.__getitem__ = Mock(
                return_value=mock_projects
            )

            query = ProjectQuery()
            result = query.__class__.__dict__["search_projects"](query, query="test")

            assert result == mock_projects

    def test_search_projects_query_too_short(self):
        """Test search_projects returns empty for query < MIN_SEARCH_QUERY_LENGTH."""
        query = ProjectQuery()
        result = query.__class__.__dict__["search_projects"](query, query="ab")

        assert result == []

    def test_search_projects_query_too_long(self):
        """Test search_projects returns empty for query > MAX_SEARCH_QUERY_LENGTH."""
        query = ProjectQuery()
        long_query = "a" * 101
        result = query.__class__.__dict__["search_projects"](query, query=long_query)

        assert result == []

    def test_search_projects_whitespace_trimmed(self):
        """Test search_projects trims whitespace before checking length."""
        query = ProjectQuery()
        result = query.__class__.__dict__["search_projects"](query, query="  ab  ")

        assert result == []


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
            mock_filter.return_value.values_list.return_value = [["testuser"], ["other-leader"]]

            query = ProjectQuery()
            result = query.__class__.__dict__["is_project_leader"](
                query, info=mock_info, login="testuser"
            )

            assert result

    def test_is_project_leader_partial_substring_does_not_match(self, mock_info):
        """Test is_project_leader avoids false positives from substring matches."""
        mock_user = Mock()
        mock_user.login = "ann"
        mock_user.name = None

        with (
            patch(
                "apps.owasp.api.internal.queries.project.GithubUser.objects.get"
            ) as mock_get_user,
            patch("apps.owasp.models.project.Project.objects.filter") as mock_filter,
        ):
            mock_get_user.return_value = mock_user
            mock_filter.return_value.values_list.return_value = [["joann"]]

            query = ProjectQuery()
            result = query.__class__.__dict__["is_project_leader"](
                query, info=mock_info, login="ann"
            )

            assert not result

    def test_is_project_leader_case_insensitive_exact_match(self, mock_info):
        """Test is_project_leader supports case-insensitive exact token matching."""
        mock_user = Mock()
        mock_user.login = "joann"
        mock_user.name = None

        with (
            patch(
                "apps.owasp.api.internal.queries.project.GithubUser.objects.get"
            ) as mock_get_user,
            patch("apps.owasp.models.project.Project.objects.filter") as mock_filter,
        ):
            mock_get_user.return_value = mock_user
            mock_filter.return_value.values_list.return_value = [["JoAnn"]]

            query = ProjectQuery()
            result = query.__class__.__dict__["is_project_leader"](
                query, info=mock_info, login="joann"
            )

            assert result
