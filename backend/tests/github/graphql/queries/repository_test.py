"""Test cases for RepositoryQuery."""

from unittest.mock import Mock, patch

import pytest

from apps.github.graphql.queries.repository import RepositoryQuery
from apps.owasp.models.project import Project


class TestRepositoryQuery:
    """Test cases for RepositoryQuery class."""

    @pytest.fixture()
    def mock_info(self):
        """GraphQL info mock fixture."""
        return Mock()

    @pytest.fixture()
    def mock_project(self):
        """Project mock fixture."""
        return Mock(spec=Project)

    def test_resolve_repository_existing(self, mock_project, mock_info):
        """Test resolving an existing repository."""
        mock_repository = Mock()
        mock_project.repositories.filter.return_value.first.return_value = mock_repository

        with patch("apps.owasp.models.project.Project.objects.get") as mock_get:
            mock_get.return_value = mock_project

            result = RepositoryQuery.resolve_repository(
                None, mock_info, project_key="test-project", repository_key="test-repo"
            )

            assert result == mock_repository
            mock_get.assert_called_once_with(key="test-project")
            mock_project.repositories.filter.assert_called_once_with(key="test-repo")

    def test_resolve_repository_not_found_project(self, mock_info):
        """Test resolving a non-existent project."""
        with patch("apps.owasp.models.project.Project.objects.get") as mock_get:
            mock_get.side_effect = Project.DoesNotExist

            result = RepositoryQuery.resolve_repository(
                None, mock_info, project_key="non-existent-project", repository_key="test-repo"
            )

            assert result is None
            mock_get.assert_called_once_with(key="non-existent-project")

    def test_resolve_repository_not_found_repository(self, mock_project, mock_info):
        """Test resolving a non-existent repository in an existing project."""
        mock_project.repositories.filter.return_value.first.return_value = None

        with patch("apps.owasp.models.project.Project.objects.get") as mock_get:
            mock_get.return_value = mock_project

            result = RepositoryQuery.resolve_repository(
                None, mock_info, project_key="test-project", repository_key="non-existent-repo"
            )

            assert result is None
            mock_get.assert_called_once_with(key="test-project")
            mock_project.repositories.filter.assert_called_once_with(key="non-existent-repo")
