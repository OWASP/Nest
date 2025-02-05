"""Test cases for RepositoryQuery."""

from unittest.mock import Mock, patch
import pytest
from graphene import Field, NonNull, String

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.repository import RepositoryNode
from apps.github.graphql.queries.repository import RepositoryQuery
from apps.github.models.repository import Repository


class TestRepositoryQuery:
    """Test cases for RepositoryQuery class."""

    @pytest.fixture()
    def mock_info(self):
        """GraphQL info mock fixture."""
        return Mock()

    def test_resolve_repository_existing(self, mock_info):
        """Test resolving an existing repository."""
        mock_repository = Mock(spec=Repository)
        mock_repository.key = "valid-repo-key"
        mock_repository.name = "Test Repository"
        mock_repository.description = "Test Description"
        
        with patch("apps.github.models.repository.Repository.objects.get") as mock_get:
            mock_get.return_value = mock_repository

            result = RepositoryQuery.resolve_repository(None, mock_info, key="valid-repo-key")

            assert result == mock_repository
            mock_get.assert_called_once_with(key="valid-repo-key")

    def test_resolve_repository_not_found(self, mock_info):
        """Test resolving a non-existent repository."""
        with patch("apps.github.models.repository.Repository.objects.get") as mock_get:
            mock_get.side_effect = Repository.DoesNotExist

            result = RepositoryQuery.resolve_repository(None, mock_info, key="invalid-repo-key")

            assert result is None
            mock_get.assert_called_once_with(key="invalid-repo-key")
