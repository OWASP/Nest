"""Tests for the OWASP dataloader aggregator."""

import pytest
from strawberry.dataloader import DataLoader

from apps.owasp.api.internal.dataloaders import get_owasp_dataloaders
from apps.owasp.api.internal.dataloaders.board_of_directors import (
    CANDIDATES_BY_BOARD_ID_LOADER,
    MEMBERS_BY_BOARD_ID_LOADER,
)
from apps.owasp.api.internal.dataloaders.project import (
    HEALTH_METRICS_LATEST_BY_PROJECT_ID,
    HEALTH_METRICS_LIST_BY_PROJECT_ID,
    PROJECT_BY_REPOSITORY_ID_LOADER,
)
from apps.owasp.api.internal.dataloaders.snapshot import (
    NEW_CHAPTERS_BY_SNAPSHOT_ID,
    NEW_ISSUES_BY_SNAPSHOT_ID,
    NEW_PROJECTS_BY_SNAPSHOT_ID,
    NEW_RELEASES_BY_SNAPSHOT_ID,
    NEW_USERS_BY_SNAPSHOT_ID,
)

EXPECTED_LOADER_KEYS = (
    CANDIDATES_BY_BOARD_ID_LOADER,
    MEMBERS_BY_BOARD_ID_LOADER,
    PROJECT_BY_REPOSITORY_ID_LOADER,
    HEALTH_METRICS_LIST_BY_PROJECT_ID,
    HEALTH_METRICS_LATEST_BY_PROJECT_ID,
    NEW_CHAPTERS_BY_SNAPSHOT_ID,
    NEW_ISSUES_BY_SNAPSHOT_ID,
    NEW_PROJECTS_BY_SNAPSHOT_ID,
    NEW_RELEASES_BY_SNAPSHOT_ID,
    NEW_USERS_BY_SNAPSHOT_ID,
)


class TestGetOwaspDataloaders:
    """Tests for get_owasp_dataloaders."""

    def test_returns_all_expected_loader_keys(self):
        """Every loader key from each sub-module is registered in the aggregated dict."""
        loaders = get_owasp_dataloaders()
        assert set(EXPECTED_LOADER_KEYS).issubset(loaders.keys())

    @pytest.mark.parametrize("loader_key", EXPECTED_LOADER_KEYS)
    def test_each_loader_is_a_dataloader_instance(self, loader_key):
        """Each registered loader is a strawberry DataLoader instance."""
        loaders = get_owasp_dataloaders()
        assert isinstance(loaders[loader_key], DataLoader)

    def test_returns_new_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_owasp_dataloaders()
        loaders2 = get_owasp_dataloaders()
        assert loaders1 is not loaders2
        for key in EXPECTED_LOADER_KEYS:
            assert loaders1[key] is not loaders2[key]
