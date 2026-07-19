"""Tests for milestone dataloaders."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from strawberry.dataloader import DataLoader

from apps.github.api.internal.dataloaders.milestone import (
    RECENT_MILESTONES_BY_PROGRAM_ID,
    RECENT_MILESTONES_BY_PROJECT_ID,
    RECENT_MILESTONES_BY_REPOSITORY_ID_LOADER,
    get_milestone_loaders,
    load_recent_milestones_by_program_id,
    load_recent_milestones_by_project_id,
    load_recent_milestones_by_repository_id,
)


class TestLoadRecentMilestonesByProgramId:
    """Tests for load_recent_milestones_by_program_id."""

    @patch("apps.github.api.internal.dataloaders.milestone.Milestone")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_milestone):
        """Queryset is built with filter, select_related, prefetch_related, order_by, distinct."""
        mock_filter_result = mock_milestone.open_milestones.filter.return_value
        mock_select_result = mock_filter_result.select_related.return_value
        mock_chain = mock_select_result.prefetch_related.return_value.order_by.return_value
        mock_chain.distinct.return_value = qs = MagicMock()
        qs.__aiter__.return_value = iter([])

        await load_recent_milestones_by_program_id([1, 2])

        mock_milestone.open_milestones.filter.assert_called_once()
        mock_filter_result.select_related.assert_called_once_with(
            "repository__organization",
            "author",
        )
        mock_select_result.prefetch_related.assert_called_once()
        mock_select_result.prefetch_related.return_value.order_by.assert_called_once_with(
            "-created_at"
        )
        mock_select_result.prefetch_related.return_value.order_by.return_value.distinct.assert_called_once()

    @patch("apps.github.api.internal.dataloaders.milestone.Milestone")
    @pytest.mark.asyncio
    async def test_maps_program_ids_to_milestones(self, mock_milestone):
        """Milestones are mapped to program IDs via repository -> project -> module chain."""
        mock_program_1 = MagicMock(pk=101)
        mock_program_2 = MagicMock(pk=102)

        mock_module_1 = MagicMock(prefetched_program=mock_program_1)
        mock_module_2 = MagicMock(prefetched_program=mock_program_2)

        mock_project_1 = MagicMock()
        mock_project_1.module_set.all.return_value = [mock_module_1]
        mock_project_2 = MagicMock()
        mock_project_2.module_set.all.return_value = [mock_module_2]

        milestone_1 = MagicMock()
        milestone_1.repository.project_set.all.return_value = [mock_project_1]
        milestone_2 = MagicMock()
        milestone_2.repository.project_set.all.return_value = [mock_project_2]

        mock_qs = mock_milestone.open_milestones.filter.return_value.select_related.return_value
        mock_qs.prefetch_related.return_value.order_by.return_value.distinct.return_value = qs = (
            MagicMock()
        )
        qs.__aiter__.return_value = iter([milestone_1, milestone_2])

        result = await load_recent_milestones_by_program_id([101, 102])

        assert result == [[milestone_1], [milestone_2]]

    @patch("apps.github.api.internal.dataloaders.milestone.Milestone")
    @pytest.mark.asyncio
    async def test_multiple_milestones_per_program(self, mock_milestone):
        """Multiple milestones for the same program are collected into one list."""
        mock_program = MagicMock(pk=201)
        mock_module = MagicMock(prefetched_program=mock_program)
        mock_project = MagicMock()
        mock_project.module_set.all.return_value = [mock_module]

        milestone_a = MagicMock()
        milestone_a.repository.project_set.all.return_value = [mock_project]
        milestone_b = MagicMock()
        milestone_b.repository.project_set.all.return_value = [mock_project]

        mock_qs = mock_milestone.open_milestones.filter.return_value.select_related.return_value
        mock_qs.prefetch_related.return_value.order_by.return_value.distinct.return_value = qs = (
            MagicMock()
        )
        qs.__aiter__.return_value = iter([milestone_a, milestone_b])

        result = await load_recent_milestones_by_program_id([201])

        assert result == [[milestone_a, milestone_b]]

    @patch("apps.github.api.internal.dataloaders.milestone.Milestone")
    @pytest.mark.asyncio
    async def test_order_matches_keys_not_queryset(self, mock_milestone):
        """The output order follows program_ids, not the milestone iteration order."""
        mock_program_1 = MagicMock(pk=1)
        mock_program_2 = MagicMock(pk=2)
        mock_module_1 = MagicMock(prefetched_program=mock_program_1)
        mock_module_2 = MagicMock(prefetched_program=mock_program_2)
        mock_project_1 = MagicMock()
        mock_project_1.module_set.all.return_value = [mock_module_1]
        mock_project_2 = MagicMock()
        mock_project_2.module_set.all.return_value = [mock_module_2]

        milestone_2 = MagicMock()
        milestone_2.repository.project_set.all.return_value = [mock_project_2]
        milestone_1 = MagicMock()
        milestone_1.repository.project_set.all.return_value = [mock_project_1]

        mock_qs = mock_milestone.open_milestones.filter.return_value.select_related.return_value
        mock_qs.prefetch_related.return_value.order_by.return_value.distinct.return_value = qs = (
            MagicMock()
        )
        qs.__aiter__.return_value = iter([milestone_2, milestone_1])

        result = await load_recent_milestones_by_program_id([1, 2])

        assert result == [[milestone_1], [milestone_2]]

    @patch("apps.github.api.internal.dataloaders.milestone.Milestone")
    @pytest.mark.asyncio
    async def test_empty_program_ids(self, mock_milestone):
        """An empty program_ids list returns an empty list."""
        mock_qs = mock_milestone.open_milestones.filter.return_value.select_related.return_value
        mock_qs.prefetch_related.return_value.order_by.return_value.distinct.return_value = qs = (
            MagicMock()
        )
        qs.__aiter__.return_value = iter([])

        result = await load_recent_milestones_by_program_id([])

        assert result == []

    @patch("apps.github.api.internal.dataloaders.milestone.Milestone")
    @pytest.mark.asyncio
    async def test_program_without_milestone_returns_empty_list(self, mock_milestone):
        """A program ID with no matching milestone gets an empty list."""
        mock_qs = mock_milestone.open_milestones.filter.return_value.select_related.return_value
        mock_qs.prefetch_related.return_value.order_by.return_value.distinct.return_value = qs = (
            MagicMock()
        )
        qs.__aiter__.return_value = iter([])

        result = await load_recent_milestones_by_program_id([99])

        assert result == [[]]


class TestLoadRecentMilestonesByRepositoryId:
    """Tests for load_recent_milestones_by_repository_id."""

    @patch(
        "apps.github.api.internal.dataloaders.milestone.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.milestone.Milestone")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(
        self, mock_milestone, mock_get_results_by_keys
    ):
        """Queryset is built with filter, annotate, and order_by."""
        keys = [(1, 5), (2, 5), (3, 5)]
        mock_qs = MagicMock()
        mock_filter = mock_milestone.objects.filter.return_value
        mock_filter.annotate.return_value.filter.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[], [], []]

        await load_recent_milestones_by_repository_id(keys)

        mock_milestone.objects.filter.assert_called_once_with(repository_id__in=[1, 2, 3])
        mock_milestone.objects.filter.return_value.annotate.assert_called_once()
        mock_milestone.objects.filter.return_value.annotate.return_value.filter.assert_called_once_with(
            row_number__lte=5
        )
        mock_milestone.objects.filter.return_value.annotate.return_value.filter.return_value.order_by.assert_called_once_with(
            "repository_id", "-created_at"
        )

    @patch(
        "apps.github.api.internal.dataloaders.milestone.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.milestone.Milestone")
    @pytest.mark.asyncio
    async def test_delegates_to_get_results_by_keys_correct_args(
        self, mock_milestone, mock_get_results_by_keys
    ):
        """get_results_by_keys receives the queryset, ids, and correct key_field."""
        keys = [(10, 5), (20, 5)]
        mock_qs = MagicMock()
        mock_filter = mock_milestone.objects.filter.return_value
        mock_filter.annotate.return_value.filter.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[], []]

        await load_recent_milestones_by_repository_id(keys)

        mock_get_results_by_keys.assert_called_once_with(
            mock_qs, [10, 20], key_field="repository_id"
        )

    @patch(
        "apps.github.api.internal.dataloaders.milestone.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.milestone.Milestone")
    @pytest.mark.asyncio
    async def test_limits_via_window_filter(self, mock_milestone, mock_get_results_by_keys):
        """The window function filter enforces the limit."""
        keys = [(1, 3)]
        mock_qs = MagicMock()
        mock_filter = mock_milestone.objects.filter.return_value
        mock_filter.annotate.return_value.filter.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[MagicMock(), MagicMock(), MagicMock()]]

        result = await load_recent_milestones_by_repository_id(keys)

        mock_milestone.objects.filter.return_value.annotate.return_value.filter.assert_called_once_with(
            row_number__lte=3
        )
        assert len(result[0]) == 3

    @patch(
        "apps.github.api.internal.dataloaders.milestone.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.milestone.Milestone")
    @pytest.mark.asyncio
    async def test_returns_result_from_get_results_by_keys(
        self, mock_milestone, mock_get_results_by_keys
    ):
        """The return value is what get_results_by_keys resolves to."""
        keys = [(1, 5)]
        mock_qs = MagicMock()
        mock_filter = mock_milestone.objects.filter.return_value
        mock_filter.annotate.return_value.filter.return_value.order_by.return_value = mock_qs
        mock_milestone_obj = MagicMock()
        expected = [[mock_milestone_obj]]
        mock_get_results_by_keys.return_value = expected

        result = await load_recent_milestones_by_repository_id(keys)

        assert result == expected

    @patch(
        "apps.github.api.internal.dataloaders.milestone.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.milestone.Milestone")
    @pytest.mark.asyncio
    async def test_empty_keys(self, mock_milestone, mock_get_results_by_keys):
        """An empty keys list returns an empty list."""
        mock_milestone.objects.filter.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = []

        result = await load_recent_milestones_by_repository_id([])

        assert result == []

    @patch(
        "apps.github.api.internal.dataloaders.milestone.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.milestone.Milestone")
    @pytest.mark.asyncio
    async def test_single_key(self, mock_milestone, mock_get_results_by_keys):
        """A single-element keys list is handled correctly end-to-end."""
        keys = [(42, 5)]
        mock_qs = MagicMock()
        mock_filter = mock_milestone.objects.filter.return_value
        mock_filter.annotate.return_value.filter.return_value.order_by.return_value = mock_qs
        mock_milestone_obj = MagicMock()
        mock_get_results_by_keys.return_value = [[mock_milestone_obj]]

        result = await load_recent_milestones_by_repository_id(keys)

        mock_milestone.objects.filter.assert_called_once_with(repository_id__in=[42])
        assert result == [[mock_milestone_obj]]

    @patch(
        "apps.github.api.internal.dataloaders.milestone.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.milestone.Milestone")
    @pytest.mark.asyncio
    async def test_repository_without_milestones_returns_empty_list(
        self, mock_milestone, mock_get_results_by_keys
    ):
        """A repository ID with no matching milestones gets an empty list."""
        keys = [(99, 5)]
        mock_qs = MagicMock()
        mock_filter = mock_milestone.objects.filter.return_value
        mock_filter.annotate.return_value.filter.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[]]

        result = await load_recent_milestones_by_repository_id(keys)

        assert result == [[]]


class TestGetMilestoneLoaders:
    """Tests for get_milestone_loaders."""

    def test_returns_mapping(self):
        """Factory always returns a Mapping."""
        loaders = get_milestone_loaders()
        for key in [
            RECENT_MILESTONES_BY_PROGRAM_ID,
            RECENT_MILESTONES_BY_REPOSITORY_ID_LOADER,
            RECENT_MILESTONES_BY_PROJECT_ID,
        ]:
            assert key in loaders
            assert isinstance(loaders[key], DataLoader)

    def test_returns_new_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_milestone_loaders()
        loaders2 = get_milestone_loaders()
        assert loaders1 is not loaders2
        for key in [
            RECENT_MILESTONES_BY_PROGRAM_ID,
            RECENT_MILESTONES_BY_REPOSITORY_ID_LOADER,
            RECENT_MILESTONES_BY_PROJECT_ID,
        ]:
            assert loaders1[key] is not loaders2[key]

    def test_load_fn_is_load_recent_milestones_by_program_id(self):
        """The milestone loader is wired to load_recent_milestones_by_program_id."""
        loaders = get_milestone_loaders()
        loader = loaders[RECENT_MILESTONES_BY_PROGRAM_ID]
        assert loader.load_fn is load_recent_milestones_by_program_id

    def test_load_fn_is_load_recent_milestones_by_repository_id(self):
        """The repository milestone loader is wired to load_recent_milestones_by_repository_id."""
        loaders = get_milestone_loaders()
        loader = loaders[RECENT_MILESTONES_BY_REPOSITORY_ID_LOADER]
        assert loader.load_fn is load_recent_milestones_by_repository_id

    def test_load_fn_is_load_recent_milestones_by_project_id(self):
        """The project milestone loader is wired to load_recent_milestones_by_project_id."""
        loaders = get_milestone_loaders()
        loader = loaders[RECENT_MILESTONES_BY_PROJECT_ID]
        assert loader.load_fn is load_recent_milestones_by_project_id


class TestLoadRecentMilestonesByProjectId:
    """Tests for load_recent_milestones_by_project_id."""

    @staticmethod
    def _ordered_qs(mock_milestone):
        """Return the mock queryset at the end of the milestones chain."""
        call = mock_milestone.objects.filter.return_value
        return call.prefetch_related.return_value.order_by.return_value

    @patch("apps.github.api.internal.dataloaders.milestone.Milestone")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_milestone):
        """Queryset is built with filter, prefetch_related, order_by, distinct."""
        mock_filter_result = mock_milestone.objects.filter.return_value
        mock_ordered = self._ordered_qs(mock_milestone)
        mock_ordered.distinct.return_value = MagicMock()
        mock_ordered.distinct.return_value.__aiter__.return_value = iter([])

        await load_recent_milestones_by_project_id([(1, 5), (2, 5)])

        mock_milestone.objects.filter.assert_called_once_with(repository__project__in=[1, 2])
        mock_filter_result.prefetch_related.assert_called_once()
        mock_filter_result.prefetch_related.return_value.order_by.assert_called_once_with(
            "-created_at"
        )
        mock_ordered.distinct.assert_called_once()

    @patch("apps.github.api.internal.dataloaders.milestone.Milestone")
    @pytest.mark.asyncio
    async def test_maps_milestones_to_project_ids(self, mock_milestone):
        """Milestones are mapped to the projects that own the milestone's repository."""
        project_1 = MagicMock(pk=1)
        project_2 = MagicMock(pk=2)
        milestone_a = MagicMock()
        milestone_a.repository.prefetched_projects = [project_1]
        milestone_b = MagicMock()
        milestone_b.repository.prefetched_projects = [project_2]

        mock_ordered = self._ordered_qs(mock_milestone)
        mock_ordered.distinct.return_value.__aiter__.return_value = iter(
            [milestone_a, milestone_b]
        )

        result = await load_recent_milestones_by_project_id([(1, 5), (2, 5)])

        assert result == [[milestone_a], [milestone_b]]

    @patch("apps.github.api.internal.dataloaders.milestone.Milestone")
    @pytest.mark.asyncio
    async def test_limit_enforced_per_project(self, mock_milestone):
        """Each project list is truncated to the configured limit."""
        project = MagicMock(pk=1)
        milestones = [MagicMock() for _ in range(5)]
        for milestone in milestones:
            milestone.repository.prefetched_projects = [project]

        mock_ordered = self._ordered_qs(mock_milestone)
        mock_ordered.distinct.return_value.__aiter__.return_value = iter(milestones)

        result = await load_recent_milestones_by_project_id([(1, 3)])

        assert result == [[milestones[0], milestones[1], milestones[2]]]

    @patch("apps.github.api.internal.dataloaders.milestone.Milestone")
    @pytest.mark.asyncio
    async def test_order_matches_keys_not_queryset(self, mock_milestone):
        """The output order follows project_ids, not the queryset iteration order."""
        project_1 = MagicMock(pk=1)
        project_2 = MagicMock(pk=2)
        milestone_b = MagicMock()
        milestone_b.repository.prefetched_projects = [project_2]
        milestone_a = MagicMock()
        milestone_a.repository.prefetched_projects = [project_1]

        mock_ordered = self._ordered_qs(mock_milestone)
        mock_ordered.distinct.return_value.__aiter__.return_value = iter(
            [milestone_b, milestone_a]
        )

        result = await load_recent_milestones_by_project_id([(1, 5), (2, 5)])

        assert result == [[milestone_a], [milestone_b]]

    @patch("apps.github.api.internal.dataloaders.milestone.Milestone")
    @pytest.mark.asyncio
    async def test_shared_repository_appears_in_each_project(self, mock_milestone):
        """A repo shared between projects contributes the milestone to each project."""
        project_1 = MagicMock(pk=1)
        project_2 = MagicMock(pk=2)
        milestone = MagicMock()
        milestone.repository.prefetched_projects = [project_1, project_2]

        mock_ordered = self._ordered_qs(mock_milestone)
        mock_ordered.distinct.return_value.__aiter__.return_value = iter([milestone])

        result = await load_recent_milestones_by_project_id([(1, 5), (2, 5)])

        assert result == [[milestone], [milestone]]

    @pytest.mark.asyncio
    async def test_empty_keys(self):
        """An empty keys list returns an empty list."""
        result = await load_recent_milestones_by_project_id([])
        assert result == []

    @patch("apps.github.api.internal.dataloaders.milestone.Milestone")
    @pytest.mark.asyncio
    async def test_missing_project_returns_empty_list(self, mock_milestone):
        """A project ID with no matching milestones gets an empty list."""
        mock_ordered = self._ordered_qs(mock_milestone)
        mock_ordered.distinct.return_value.__aiter__.return_value = iter([])

        result = await load_recent_milestones_by_project_id([(99, 5)])

        assert result == [[]]
