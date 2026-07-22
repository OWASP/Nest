"""Tests for the admin dataloader."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from strawberry.dataloader import DataLoader

from apps.mentorship.api.internal.dataloaders.admin import (
    ADMINS_BY_PROGRAM_ID_LOADER,
    get_admin_loaders,
    load_admins_by_program_id,
)


class TestLoadAdminsByProgramId:
    """Tests for load_admins_by_program_id."""

    @patch(
        "apps.mentorship.api.internal.dataloaders.admin.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.mentorship.api.internal.dataloaders.admin.Admin")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(
        self, mock_admin, mock_get_results_by_keys
    ):
        """Queryset is built with select_related, filter, annotate, and order_by."""
        program_ids = [1, 2, 3]
        mock_queryset = MagicMock()
        mock_admin_filter = mock_admin.objects.select_related.return_value.filter
        mock_admin_filter.return_value.annotate.return_value.order_by.return_value = (
            mock_queryset
        )
        mock_get_results_by_keys.return_value = [[], [], []]

        await load_admins_by_program_id(program_ids)

        mock_admin.objects.select_related.assert_called_once_with("github_user")
        mock_filter = mock_admin.objects.select_related.return_value.filter
        mock_filter.assert_called_once_with(admin_programs__in=program_ids)
        mock_filter.return_value.annotate.assert_called_once()
        mock_filter.return_value.annotate.return_value.order_by.assert_called_once_with(
            "github_user__login"
        )

    @patch(
        "apps.mentorship.api.internal.dataloaders.admin.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.mentorship.api.internal.dataloaders.admin.Admin")
    @pytest.mark.asyncio
    async def test_delegates_to_get_results_by_keys_correct_args(
        self, mock_admin, mock_get_results_by_keys
    ):
        """get_results_by_keys receives the queryset, program_ids, and correct key_field."""
        program_ids = [10, 20]
        mock_queryset = MagicMock()
        mock_admin_filter = mock_admin.objects.select_related.return_value.filter
        mock_admin_filter.return_value.annotate.return_value.order_by.return_value = (
            mock_queryset
        )
        mock_get_results_by_keys.return_value = [[], []]

        await load_admins_by_program_id(program_ids)

        mock_get_results_by_keys.assert_called_once_with(
            mock_queryset, program_ids, key_field="program_id"
        )

    @patch(
        "apps.mentorship.api.internal.dataloaders.admin.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.mentorship.api.internal.dataloaders.admin.Admin")
    @pytest.mark.asyncio
    async def test_returns_result_from_get_results_by_keys(
        self, mock_admin, mock_get_results_by_keys
    ):
        """The return value is exactly what get_results_by_keys resolves to."""
        mock_admin_a = MagicMock()
        mock_admin_b = MagicMock()
        expected = [[mock_admin_a, mock_admin_b], [], [mock_admin_a]]
        mock_admin_filter = mock_admin.objects.select_related.return_value.filter
        mock_admin_filter.return_value.annotate.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = expected

        result = await load_admins_by_program_id([1, 2, 3])

        assert result is expected

    @patch(
        "apps.mentorship.api.internal.dataloaders.admin.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.mentorship.api.internal.dataloaders.admin.Admin")
    @pytest.mark.asyncio
    async def test_empty_program_ids(self, mock_admin, mock_get_results_by_keys):
        """An empty program_ids list results in an empty filter and empty return."""
        mock_admin_filter = mock_admin.objects.select_related.return_value.filter
        mock_admin_filter.return_value.annotate.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = []

        result = await load_admins_by_program_id([])

        mock_admin.objects.select_related.return_value.filter.assert_called_once_with(
            admin_programs__in=[]
        )
        assert result == []

    @patch(
        "apps.mentorship.api.internal.dataloaders.admin.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.mentorship.api.internal.dataloaders.admin.Admin")
    @pytest.mark.asyncio
    async def test_single_program_id(self, mock_admin, mock_get_results_by_keys):
        """A single-element list is handled correctly end-to-end."""
        mock_admin_obj = MagicMock()
        mock_admin_filter = mock_admin.objects.select_related.return_value.filter
        mock_admin_filter.return_value.annotate.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = [[mock_admin_obj]]

        result = await load_admins_by_program_id([42])

        mock_admin.objects.select_related.return_value.filter.assert_called_once_with(
            admin_programs__in=[42]
        )
        assert result == [[mock_admin_obj]]


class TestGetAdminLoaders:
    """Tests for get_admin_loaders."""

    def test_returns_mapping(self):
        """Factory always returns a Mapping."""
        loaders = get_admin_loaders()
        assert ADMINS_BY_PROGRAM_ID_LOADER in loaders
        assert isinstance(loaders[ADMINS_BY_PROGRAM_ID_LOADER], DataLoader)

    def test_returns_new_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_admin_loaders()
        loaders2 = get_admin_loaders()
        assert loaders1 is not loaders2
        assert loaders1[ADMINS_BY_PROGRAM_ID_LOADER] is not loaders2[ADMINS_BY_PROGRAM_ID_LOADER]

    def test_load_fn_is_load_admins_by_program_id(self):
        """The by-program-id DataLoader is wired to load_admins_by_program_id."""
        loaders = get_admin_loaders()
        loader = loaders[ADMINS_BY_PROGRAM_ID_LOADER]
        assert loader.load_fn is load_admins_by_program_id
