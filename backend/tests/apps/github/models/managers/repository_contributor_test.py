from unittest.mock import MagicMock, patch

import pytest

from apps.github.models.managers.repository_contributor import (
    RepositoryContributorManager,
    RepositoryContributorQuerySet,
)
from apps.github.models.user import User


class TestRepositoryContributorQuerySet:
    @pytest.fixture()
    def repo_contributor_qs(self):
        return MagicMock(spec=RepositoryContributorQuerySet)

    def test_by_humans(self, repo_contributor_qs):
        mock_filter = MagicMock()
        mock_exclude = MagicMock()

        repo_contributor_qs.filter.return_value = mock_filter
        mock_filter.exclude.return_value = mock_exclude

        with patch.object(User, "get_non_indexable_logins", return_value=["bot1", "bot2"]):
            result = RepositoryContributorQuerySet.by_humans(repo_contributor_qs)

            repo_contributor_qs.filter.assert_called_once_with(user__is_bot=False)
            mock_filter.exclude.assert_called_once_with(user__login__in=["bot1", "bot2"])
            assert result == mock_exclude


class TestRepositoryContributorManager:
    @pytest.fixture()
    def repo_contributor_manager(self):
        manager = MagicMock(spec=RepositoryContributorManager)
        manager.model = MagicMock()
        manager._db = None
        return manager

    def test_get_queryset(self, repo_contributor_manager):
        mock_queryset = MagicMock()
        mock_select_related = MagicMock()

        with patch(
            "apps.github.models.managers.repository_contributor.RepositoryContributorQuerySet"
        ) as mock_qs_class:
            mock_qs_class.return_value = mock_queryset
            mock_queryset.select_related.return_value = mock_select_related

            result = RepositoryContributorManager.get_queryset(repo_contributor_manager)

            mock_qs_class.assert_called_once_with(
                repo_contributor_manager.model,
                using=repo_contributor_manager._db,
            )
            mock_queryset.select_related.assert_called_once_with(
                "repository",
                "user",
            )
            assert result == mock_select_related

    def test_by_humans(self, repo_contributor_manager):
        mock_queryset = MagicMock()
        mock_by_humans = MagicMock()

        repo_contributor_manager.get_queryset.return_value = mock_queryset
        mock_queryset.by_humans.return_value = mock_by_humans

        result = RepositoryContributorManager.by_humans(repo_contributor_manager)

        repo_contributor_manager.get_queryset.assert_called_once()
        mock_queryset.by_humans.assert_called_once()
        assert result == mock_by_humans

    def test_to_community_repositories(self, repo_contributor_manager):
        mock_queryset = MagicMock()
        mock_to_community = MagicMock()

        repo_contributor_manager.get_queryset.return_value = mock_queryset
        mock_queryset.to_community_repositories.return_value = mock_to_community

        result = RepositoryContributorManager.to_community_repositories(repo_contributor_manager)

        repo_contributor_manager.get_queryset.assert_called_once()
        mock_queryset.to_community_repositories.assert_called_once()
        assert result == mock_to_community
