"""Test cases for RepositoryQuery."""

from unittest.mock import Mock, patch

import pytest

from apps.github.graphql.queries.repository import RepositoryQuery
from apps.github.models.repository import Repository


class TestRepositoryQuery:
    """Test cases for RepositoryQuery class."""

    @pytest.fixture()
    def mock_info(self):
        """GraphQL info mock fixture."""
        return Mock()

    @pytest.fixture()
    def mock_repository(self):
        """Repository mock fixture."""
        return Mock(spec=Repository)

    def test_resolve_repository_existing(self, mock_repository, mock_info):
        """Test resolving an existing repository."""
        with patch("apps.github.models.repository.Repository.objects.get") as mock_get:
            mock_get.return_value = mock_repository

            result = RepositoryQuery.resolve_repository(
                None, mock_info, repository_key="test-repo"
            )

            assert result == mock_repository
            mock_get.assert_called_once_with(key="test-repo")

    def test_resolve_repository_not_found(self, mock_info):
        """Test resolving a non-existent repository."""
        with patch("apps.github.models.repository.Repository.objects.get") as mock_get:
            mock_get.side_effect = Repository.DoesNotExist

            result = RepositoryQuery.resolve_repository(
                None, mock_info, repository_key="non-existent-repo"
            )

            assert result is None
            mock_get.assert_called_once_with(key="non-existent-repo")
