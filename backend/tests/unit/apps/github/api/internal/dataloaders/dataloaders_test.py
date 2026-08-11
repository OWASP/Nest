"""Tests for the GitHub dataloader aggregator."""

import pytest
from strawberry.dataloader import DataLoader

from apps.github.api.internal.dataloaders import get_github_dataloaders
from apps.github.api.internal.dataloaders.issue import (
    ISSUES_BY_REPOSITORY_ID_LOADER,
    ISSUES_COUNT_BY_PROJECT_ID_LOADER,
    OPEN_ISSUES_COUNT_BY_PROJECT_ID_LOADER,
    RECENT_ISSUES_BY_PROJECT_ID_LOADER,
)
from apps.github.api.internal.dataloaders.milestone import (
    RECENT_MILESTONES_BY_PROGRAM_ID_LOADER,
    RECENT_MILESTONES_BY_PROJECT_ID_LOADER,
    RECENT_MILESTONES_BY_REPOSITORY_ID_LOADER,
)
from apps.github.api.internal.dataloaders.pull_request import (
    RECENT_PULL_REQUESTS_BY_PROJECT_ID_LOADER,
)
from apps.github.api.internal.dataloaders.release import (
    LATEST_RELEASE_BY_REPOSITORY_ID_LOADER,
    RECENT_RELEASES_BY_PROJECT_ID_LOADER,
    RECENT_RELEASES_BY_REPOSITORY_ID_LOADER,
    RELEASE_URL_BY_ID_LOADER,
)
from apps.github.api.internal.dataloaders.repository import (
    REPOSITORIES_BY_PROJECT_ID_LOADER,
    REPOSITORIES_COUNT_BY_PROJECT_ID_LOADER,
    REPOSITORY_BY_RELEASE_ID_LOADER,
    REPOSITORY_PROJECT_NAME_BY_RELEASE_ID_LOADER,
)
from apps.github.api.internal.dataloaders.repository_contributor import (
    TOP_CONTRIBUTORS_BY_CHAPTER_ID_LOADER,
    TOP_CONTRIBUTORS_BY_PROJECT_ID_LOADER,
    TOP_CONTRIBUTORS_BY_REPOSITORY_ID_LOADER,
)
from apps.github.api.internal.dataloaders.user import (
    USER_BADGES_BY_USER_ID_LOADER,
    USER_ISSUES_COUNT_LOADER,
    USER_RELEASES_COUNT_LOADER,
)

EXPECTED_LOADER_KEYS = (
    ISSUES_BY_REPOSITORY_ID_LOADER,
    ISSUES_COUNT_BY_PROJECT_ID_LOADER,
    LATEST_RELEASE_BY_REPOSITORY_ID_LOADER,
    OPEN_ISSUES_COUNT_BY_PROJECT_ID_LOADER,
    RECENT_ISSUES_BY_PROJECT_ID_LOADER,
    RECENT_MILESTONES_BY_PROGRAM_ID_LOADER,
    RECENT_MILESTONES_BY_PROJECT_ID_LOADER,
    RECENT_MILESTONES_BY_REPOSITORY_ID_LOADER,
    RECENT_PULL_REQUESTS_BY_PROJECT_ID_LOADER,
    RECENT_RELEASES_BY_PROJECT_ID_LOADER,
    RECENT_RELEASES_BY_REPOSITORY_ID_LOADER,
    RELEASE_URL_BY_ID_LOADER,
    REPOSITORIES_BY_PROJECT_ID_LOADER,
    REPOSITORIES_COUNT_BY_PROJECT_ID_LOADER,
    REPOSITORY_BY_RELEASE_ID_LOADER,
    REPOSITORY_PROJECT_NAME_BY_RELEASE_ID_LOADER,
    TOP_CONTRIBUTORS_BY_CHAPTER_ID_LOADER,
    TOP_CONTRIBUTORS_BY_PROJECT_ID_LOADER,
    TOP_CONTRIBUTORS_BY_REPOSITORY_ID_LOADER,
    USER_BADGES_BY_USER_ID_LOADER,
    USER_ISSUES_COUNT_LOADER,
    USER_RELEASES_COUNT_LOADER,
)


class TestGetGithubDataloaders:
    """Tests for get_github_dataloaders."""

    def test_returns_all_expected_loader_keys(self):
        """Every loader key from each sub-module is registered in the aggregated dict."""
        loaders = get_github_dataloaders()
        assert set(EXPECTED_LOADER_KEYS).issubset(loaders.keys())

    @pytest.mark.parametrize("loader_key", EXPECTED_LOADER_KEYS)
    def test_each_loader_is_a_dataloader_instance(self, loader_key):
        """Each registered loader is a strawberry DataLoader instance."""
        loaders = get_github_dataloaders()
        assert isinstance(loaders[loader_key], DataLoader)

    def test_returns_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_github_dataloaders()
        loaders2 = get_github_dataloaders()
        assert loaders1 is not loaders2
        for key in EXPECTED_LOADER_KEYS:
            assert loaders1[key] is not loaders2[key]
