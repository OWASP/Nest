"""Tests for the Mentorship dataloader aggregator."""

import pytest
from strawberry.dataloader import DataLoader

from apps.mentorship.api.internal.dataloaders import get_mentorship_dataloaders
from apps.mentorship.api.internal.dataloaders.admin import ADMINS_BY_PROGRAM_ID_LOADER
from apps.mentorship.api.internal.dataloaders.interested_users import (
    INTERESTED_USERS_BY_ISSUE_ID_LOADER,
)

EXPECTED_LOADER_KEYS = (
    ADMINS_BY_PROGRAM_ID_LOADER,
    INTERESTED_USERS_BY_ISSUE_ID_LOADER,
)


class TestGetMentorshipDataloaders:
    """Tests for get_mentorship_dataloaders."""

    def test_returns_all_expected_loader_keys(self):
        """Every loader key from each sub-module is registered in the aggregated dict."""
        loaders = get_mentorship_dataloaders()
        assert set(EXPECTED_LOADER_KEYS) == set(loaders.keys())

    @pytest.mark.parametrize("loader_key", EXPECTED_LOADER_KEYS)
    def test_each_loader_is_a_dataloader_instance(self, loader_key):
        """Each registered loader is a strawberry DataLoader instance."""
        loaders = get_mentorship_dataloaders()
        assert isinstance(loaders[loader_key], DataLoader)

    def test_returns_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_mentorship_dataloaders()
        loaders2 = get_mentorship_dataloaders()
        assert loaders1 is not loaders2
        for key in EXPECTED_LOADER_KEYS:
            assert loaders1[key] is not loaders2[key]
