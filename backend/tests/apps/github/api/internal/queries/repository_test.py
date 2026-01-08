"""Test cases for RepositoryQuery."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from apps.github.api.internal.queries.repository import RepositoryQuery
from apps.github.models.repository import Repository


class TestRepositoryQuery:
    """Test cases for RepositoryQuery class."""

    @pytest.fixture
    def mock_repository(self):
        """Repository mock fixture."""
        repo = Mock(spec=Repository)
        repo.key = "test-repo"
        return repo

    def test_resolve_repository_existing(self, mock_repository):
        """Test resolving an existing repository."""
        mock_queryset = MagicMock()
        mock_queryset.select_related.return_value = mock_queryset
        mock_queryset.get.return_value = mock_repository

        with patch(
            "apps.github.models.repository.Repository.objects",
            mock_queryset,
        ):
            result = RepositoryQuery().repository(
                organization_key="test-org",
                repository_key="test-repo",
            )

            assert result == mock_repository
            mock_queryset.select_related.assert_called_once_with("organization")
            mock_queryset.get.assert_called_once_with(
                organization__login__iexact="test-org",
                key__iexact="test-repo",
            )

    def test_resolve_repository_not_found(self):
        """Test resolving a non-existent repository."""
        mock_queryset = MagicMock()
        mock_queryset.select_related.return_value = mock_queryset
        mock_queryset.get.side_effect = Repository.DoesNotExist

        with patch(
            "apps.github.models.repository.Repository.objects",
            mock_queryset,
        ):
            result = RepositoryQuery().repository(
                organization_key="non-existent-org",
                repository_key="non-existent-repo",
            )

            assert result is None
            mock_queryset.select_related.assert_called_once_with("organization")
            mock_queryset.get.assert_called_once_with(
                organization__login__iexact="non-existent-org",
                key__iexact="non-existent-repo",
            )

    def test_resolve_repositories(self, mock_repository):
        """Test resolving repositories list."""
        mock_queryset = MagicMock()
        mock_queryset.filter.return_value.order_by.return_value.__getitem__.return_value = [
            mock_repository
        ]

        with patch(
            "apps.github.models.repository.Repository.objects",
            mock_queryset,
        ):
            result = RepositoryQuery().repositories(
                organization="test-org",
                limit=1,
            )

            assert isinstance(result, list)
            assert result[0] == mock_repository
            mock_queryset.filter.assert_called_once_with(organization__login__iexact="test-org")
            mock_queryset.filter.return_value.order_by.assert_called_once_with("-stars_count")
