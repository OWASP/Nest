"""Test cases for RepositoryQuery."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from apps.github.graphql.queries.repository import RepositoryQuery
from apps.github.models.repository import Repository


class TestRepositoryQuery:
    """Test cases for RepositoryQuery class."""

    @pytest.fixture
    def mock_info(self):
        """GraphQL info mock fixture."""
        return Mock()

    @pytest.fixture
    def mock_repository(self):
        """Repository mock fixture."""
        return Mock(spec=Repository)

    def test_resolve_repository_existing(self, mock_repository, mock_info):
        """Test resolving an existing repository."""
        mock_queryset = MagicMock()
        mock_queryset.get.return_value = mock_repository

        with patch(
            "apps.github.models.repository.Repository.objects.select_related",
            return_value=mock_queryset,
        ) as mock_select_related:
            result = RepositoryQuery.resolve_repository(
                None, mock_info, repository_key="test-repo", organization_key="test-org"
            )

            assert result == mock_repository
            mock_select_related.assert_called_once_with("organization")
            mock_queryset.get.assert_called_once_with(
                key__iexact="test-repo",
                organization__login__iexact="test-org",
            )

    def test_resolve_repository_not_found(self, mock_info):
        """Test resolving a non-existent repository."""
        mock_queryset = MagicMock()
        mock_queryset.get.side_effect = Repository.DoesNotExist

        with patch(
            "apps.github.models.repository.Repository.objects.select_related",
            return_value=mock_queryset,
        ) as mock_select_related:
            result = RepositoryQuery.resolve_repository(
                None,
                mock_info,
                repository_key="non-existent-repo",
                organization_key="non-existent-org",
            )

            assert result is None
            mock_select_related.assert_called_once_with("organization")
            mock_queryset.get.assert_called_once_with(
                key__iexact="non-existent-repo",
                organization__login__iexact="non-existent-org",
            )
