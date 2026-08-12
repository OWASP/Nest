"""Tests for the OWASP dataloader aggregator."""

import pytest
from strawberry.dataloader import DataLoader

from apps.owasp.api.internal.dataloaders import get_owasp_dataloaders
from apps.owasp.api.internal.dataloaders.board_of_directors import (
    CANDIDATES_BY_BOARD_ID_LOADER,
    MEMBERS_BY_BOARD_ID_LOADER,
)
from apps.owasp.api.internal.dataloaders.chapter import (
    ENTITY_CHANNELS_BY_CHAPTER_ID_LOADER,
    ENTITY_LEADERS_BY_CHAPTER_ID_LOADER,
)
from apps.owasp.api.internal.dataloaders.committee import (
    ENTITY_CHANNELS_BY_COMMITTEE_ID_LOADER,
    ENTITY_LEADERS_BY_COMMITTEE_ID_LOADER,
)
from apps.owasp.api.internal.dataloaders.entity_channel import (
    EXTERNAL_ID_BY_ENTITY_CHANNEL_ID_LOADER,
    NAME_BY_ENTITY_CHANNEL_ID_LOADER,
)
from apps.owasp.api.internal.dataloaders.member_snapshot import (
    COMMITS_COUNT_BY_SNAPSHOT_ID_LOADER,
    ISSUES_COUNT_BY_SNAPSHOT_ID_LOADER,
    MESSAGES_COUNT_BY_SNAPSHOT_ID_LOADER,
    PULL_REQUESTS_COUNT_BY_SNAPSHOT_ID_LOADER,
    TOTAL_CONTRIBUTIONS_BY_SNAPSHOT_ID_LOADER,
)
from apps.owasp.api.internal.dataloaders.project import (
    ENTITY_CHANNELS_BY_PROJECT_ID_LOADER,
    ENTITY_LEADERS_BY_PROJECT_ID_LOADER,
    HEALTH_METRICS_LATEST_BY_PROJECT_ID_LOADER,
    HEALTH_METRICS_LIST_BY_PROJECT_ID_LOADER,
    PROJECT_BY_REPOSITORY_ID_LOADER,
)
from apps.owasp.api.internal.dataloaders.snapshot import (
    CHAPTERS_BY_SNAPSHOT_ID,
    ISSUES_BY_SNAPSHOT_ID,
    PROJECTS_BY_SNAPSHOT_ID,
    RELEASES_BY_SNAPSHOT_ID,
    USERS_BY_SNAPSHOT_ID,
)

EXPECTED_LOADER_KEYS = (
    CANDIDATES_BY_BOARD_ID_LOADER,
    CHAPTERS_BY_SNAPSHOT_ID,
    COMMITS_COUNT_BY_SNAPSHOT_ID_LOADER,
    ENTITY_CHANNELS_BY_CHAPTER_ID_LOADER,
    ENTITY_CHANNELS_BY_COMMITTEE_ID_LOADER,
    ENTITY_CHANNELS_BY_PROJECT_ID_LOADER,
    ENTITY_LEADERS_BY_CHAPTER_ID_LOADER,
    ENTITY_LEADERS_BY_COMMITTEE_ID_LOADER,
    ENTITY_LEADERS_BY_PROJECT_ID_LOADER,
    EXTERNAL_ID_BY_ENTITY_CHANNEL_ID_LOADER,
    HEALTH_METRICS_LATEST_BY_PROJECT_ID_LOADER,
    HEALTH_METRICS_LIST_BY_PROJECT_ID_LOADER,
    ISSUES_BY_SNAPSHOT_ID,
    ISSUES_COUNT_BY_SNAPSHOT_ID_LOADER,
    MEMBERS_BY_BOARD_ID_LOADER,
    MESSAGES_COUNT_BY_SNAPSHOT_ID_LOADER,
    NAME_BY_ENTITY_CHANNEL_ID_LOADER,
    PROJECTS_BY_SNAPSHOT_ID,
    PROJECT_BY_REPOSITORY_ID_LOADER,
    PULL_REQUESTS_COUNT_BY_SNAPSHOT_ID_LOADER,
    RELEASES_BY_SNAPSHOT_ID,
    TOTAL_CONTRIBUTIONS_BY_SNAPSHOT_ID_LOADER,
    USERS_BY_SNAPSHOT_ID,
)


class TestGetOwaspDataloaders:
    """Tests for get_owasp_dataloaders."""

    def test_returns_all_expected_loader_keys(self):
        """Every loader key from each sub-module is registered in the aggregated dict."""
        loaders = get_owasp_dataloaders()
        assert set(EXPECTED_LOADER_KEYS) == set(loaders.keys())

    @pytest.mark.parametrize("loader_key", EXPECTED_LOADER_KEYS)
    def test_each_loader_is_a_dataloader_instance(self, loader_key):
        """Each registered loader is a strawberry DataLoader instance."""
        loaders = get_owasp_dataloaders()
        assert isinstance(loaders[loader_key], DataLoader)

    def test_returns_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_owasp_dataloaders()
        loaders2 = get_owasp_dataloaders()
        assert loaders1 is not loaders2
        for key in EXPECTED_LOADER_KEYS:
            assert loaders1[key] is not loaders2[key]
