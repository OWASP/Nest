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

    def test_by_humans_excludes_bots(self, mocker):
        """Tests that by_humans excludes bots and non-indexable users."""
        mocker.patch("apps.github.models.user.User.get_non_indexable_logins", return_value=set())
        mock_queryset = mocker.Mock(spec=RepositoryContributorQuerySet)
        RepositoryContributorQuerySet.by_humans(mock_queryset)
        mock_queryset.exclude.assert_called_once()
        args, _ = mock_queryset.exclude.call_args
        q_object = args[0]
        assert "user__is_bot" in str(q_object)
        assert "user__login__endswith" in str(q_object)

    def test_to_community_repositories_excludes_forks_and_non_community(self, mocker):
        """Tests that to_community_repositories excludes forks and non-community repos."""
        mock_queryset = mocker.Mock(spec=RepositoryContributorQuerySet)
        RepositoryContributorQuerySet.to_community_repositories(mock_queryset)
        mock_queryset.exclude.assert_called_once()
        args, _ = mock_queryset.exclude.call_args
        q_object = args[0]
        assert "repository__is_fork" in str(q_object)
        assert "repository__organization__is_owasp_related_organization" in str(q_object)


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
