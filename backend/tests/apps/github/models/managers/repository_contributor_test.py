"""Tests for RepositoryContributor managers."""

from unittest import mock

from apps.github.models.managers.repository_contributor import (
    RepositoryContributorManager,
    RepositoryContributorQuerySet,
)


class TestRepositoryContributorQuerySet:
    def test_by_humans_method_exists(self):
        """Test that by_humans method is defined."""
        assert hasattr(RepositoryContributorQuerySet, "by_humans")
        assert callable(RepositoryContributorQuerySet.by_humans)

    def test_to_community_repositories_method_exists(self):
        """Test that to_community_repositories method is defined."""
        assert hasattr(RepositoryContributorQuerySet, "to_community_repositories")
        assert callable(RepositoryContributorQuerySet.to_community_repositories)


class TestRepositoryContributorManager:
    def test_get_queryset_returns_custom_queryset(self):
        manager = RepositoryContributorManager()
        manager.model = mock.Mock()
        manager._db = None

        with mock.patch(
            "apps.github.models.managers.repository_contributor.RepositoryContributorQuerySet"
        ) as mock_queryset_class:
            mock_queryset = mock.Mock()
            mock_queryset_class.return_value = mock_queryset
            mock_queryset.select_related.return_value = mock_queryset

            result = manager.get_queryset()

            mock_queryset.select_related.assert_called_once_with("repository", "user")
            assert result == mock_queryset

    def test_by_humans_delegates_to_queryset(self):
        manager = RepositoryContributorManager()
        manager.model = mock.Mock()

        mock_queryset = mock.Mock()

        with mock.patch.object(manager, "get_queryset", return_value=mock_queryset):
            mock_queryset.by_humans.return_value = mock_queryset

            result = manager.by_humans()

            mock_queryset.by_humans.assert_called_once()
            assert result == mock_queryset

    def test_to_community_repositories_delegates_to_queryset(self):
        manager = RepositoryContributorManager()
        manager.model = mock.Mock()

        mock_queryset = mock.Mock()

        with mock.patch.object(manager, "get_queryset", return_value=mock_queryset):
            mock_queryset.to_community_repositories.return_value = mock_queryset

            result = manager.to_community_repositories()

            mock_queryset.to_community_repositories.assert_called_once()
            assert result == mock_queryset
