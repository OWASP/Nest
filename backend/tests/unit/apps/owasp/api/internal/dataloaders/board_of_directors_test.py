"""Tests for the board of directors dataloaders."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from strawberry.dataloader import DataLoader

from apps.owasp.api.internal.dataloaders.board_of_directors import (
    CANDIDATES_BY_BOARD_ID_LOADER,
    MEMBERS_BY_BOARD_ID_LOADER,
    BoardOfDirectors,
    get_board_of_directors_loaders,
    load_candidates_by_board_id,
    load_members_by_board_id,
)


async def _async_return(value):
    return value


def _fake_sync_to_async(fn):
    return lambda *args, **kwargs: _async_return(fn(*args, **kwargs))


class TestLoadCandidatesByBoardId:
    """Tests for load_candidates_by_board_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.EntityMember")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(
        self, mock_entity_member, mock_content_type, mock_get_results_by_keys
    ):
        """Queryset is built with select_related, filter, and order_by in the right order."""
        board_ids = [1, 2, 3]
        mock_content_type_obj = MagicMock()
        mock_content_type.objects.get_for_model.return_value = mock_content_type_obj
        mock_queryset = MagicMock()
        mock_filter = mock_entity_member.objects.select_related.return_value.filter
        mock_filter.return_value.order_by.return_value = mock_queryset
        mock_get_results_by_keys.return_value = [[], [], []]

        await load_candidates_by_board_id(board_ids)

        mock_entity_member.objects.select_related.assert_called_once_with("member")
        mock_filter.assert_called_once_with(
            entity_type=mock_content_type_obj,
            entity_id__in=board_ids,
            role=mock_entity_member.Role.CANDIDATE,
            is_active=True,
            is_reviewed=True,
        )
        mock_filter.return_value.order_by.assert_called_once_with("member_name")

    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.EntityMember")
    @pytest.mark.asyncio
    async def test_delegates_to_get_results_by_keys_correct_args(
        self, mock_entity_member, mock_content_type, mock_get_results_by_keys
    ):
        """get_results_by_keys receives the queryset, board_ids, and correct key_field."""
        board_ids = [10, 20]
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_queryset = MagicMock()
        mock_filter = mock_entity_member.objects.select_related.return_value.filter
        mock_filter.return_value.order_by.return_value = mock_queryset
        mock_get_results_by_keys.return_value = [[], []]

        await load_candidates_by_board_id(board_ids)

        mock_get_results_by_keys.assert_called_once_with(
            mock_queryset, board_ids, key_field="entity_id"
        )

    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.EntityMember")
    @pytest.mark.asyncio
    async def test_returns_result_from_get_results_by_keys(
        self, mock_entity_member, mock_content_type, mock_get_results_by_keys
    ):
        """The return value is exactly what get_results_by_keys resolves to."""
        mock_candidate_a = MagicMock()
        mock_candidate_b = MagicMock()
        expected = [[mock_candidate_a, mock_candidate_b], [], [mock_candidate_a]]
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_filter = mock_entity_member.objects.select_related.return_value.filter
        mock_filter.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = expected

        result = await load_candidates_by_board_id([1, 2, 3])

        assert result is expected

    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.EntityMember")
    @pytest.mark.asyncio
    async def test_empty_board_ids(
        self, mock_entity_member, mock_content_type, mock_get_results_by_keys
    ):
        """An empty board_ids list results in an empty filter and empty return."""
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_filter = mock_entity_member.objects.select_related.return_value.filter
        mock_filter.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = []

        result = await load_candidates_by_board_id([])

        mock_filter.assert_called_once_with(
            entity_type=mock_content_type.objects.get_for_model.return_value,
            entity_id__in=[],
            role=mock_entity_member.Role.CANDIDATE,
            is_active=True,
            is_reviewed=True,
        )
        assert result == []

    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.EntityMember")
    @pytest.mark.asyncio
    async def test_single_board_id(
        self, mock_entity_member, mock_content_type, mock_get_results_by_keys
    ):
        """A single-element list is handled correctly end-to-end."""
        mock_candidate = MagicMock()
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_filter = mock_entity_member.objects.select_related.return_value.filter
        mock_filter.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = [[mock_candidate]]

        result = await load_candidates_by_board_id([42])

        mock_filter.assert_called_once_with(
            entity_type=mock_content_type.objects.get_for_model.return_value,
            entity_id__in=[42],
            role=mock_entity_member.Role.CANDIDATE,
            is_active=True,
            is_reviewed=True,
        )
        assert result == [[mock_candidate]]

    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.EntityMember")
    @pytest.mark.asyncio
    async def test_uses_board_of_directors_content_type(
        self, mock_entity_member, mock_content_type, mock_get_results_by_keys
    ):
        """ContentType.objects.get_for_model is called with BoardOfDirectors."""
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_filter = mock_entity_member.objects.select_related.return_value.filter
        mock_filter.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = [[]]

        await load_candidates_by_board_id([1])

        mock_content_type.objects.get_for_model.assert_called_once_with(BoardOfDirectors)


class TestLoadMembersByBoardId:
    """Tests for load_members_by_board_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.EntityMember")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(
        self, mock_entity_member, mock_content_type, mock_get_results_by_keys
    ):
        """Queryset is built with select_related, filter, and order_by in the right order."""
        board_ids = [1, 2, 3]
        mock_content_type_obj = MagicMock()
        mock_content_type.objects.get_for_model.return_value = mock_content_type_obj
        mock_queryset = MagicMock()
        mock_filter = mock_entity_member.objects.select_related.return_value.filter
        mock_filter.return_value.order_by.return_value = mock_queryset
        mock_get_results_by_keys.return_value = [[], [], []]

        await load_members_by_board_id(board_ids)

        mock_entity_member.objects.select_related.assert_called_once_with("member")
        mock_filter.assert_called_once_with(
            entity_type=mock_content_type_obj,
            entity_id__in=board_ids,
            role=mock_entity_member.Role.MEMBER,
            is_active=True,
            is_reviewed=True,
        )
        mock_filter.return_value.order_by.assert_called_once_with("member_name")

    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.EntityMember")
    @pytest.mark.asyncio
    async def test_delegates_to_get_results_by_keys_correct_args(
        self, mock_entity_member, mock_content_type, mock_get_results_by_keys
    ):
        """get_results_by_keys receives the queryset, board_ids, and correct key_field."""
        board_ids = [10, 20]
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_queryset = MagicMock()
        mock_filter = mock_entity_member.objects.select_related.return_value.filter
        mock_filter.return_value.order_by.return_value = mock_queryset
        mock_get_results_by_keys.return_value = [[], []]

        await load_members_by_board_id(board_ids)

        mock_get_results_by_keys.assert_called_once_with(
            mock_queryset, board_ids, key_field="entity_id"
        )

    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.EntityMember")
    @pytest.mark.asyncio
    async def test_returns_result_from_get_results_by_keys(
        self, mock_entity_member, mock_content_type, mock_get_results_by_keys
    ):
        """The return value is exactly what get_results_by_keys resolves to."""
        mock_member_a = MagicMock()
        mock_member_b = MagicMock()
        expected = [[mock_member_a, mock_member_b], [], [mock_member_a]]
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_filter = mock_entity_member.objects.select_related.return_value.filter
        mock_filter.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = expected

        result = await load_members_by_board_id([1, 2, 3])

        assert result is expected

    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.EntityMember")
    @pytest.mark.asyncio
    async def test_empty_board_ids(
        self, mock_entity_member, mock_content_type, mock_get_results_by_keys
    ):
        """An empty board_ids list results in an empty filter and empty return."""
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_filter = mock_entity_member.objects.select_related.return_value.filter
        mock_filter.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = []

        result = await load_members_by_board_id([])

        mock_filter.assert_called_once_with(
            entity_type=mock_content_type.objects.get_for_model.return_value,
            entity_id__in=[],
            role=mock_entity_member.Role.MEMBER,
            is_active=True,
            is_reviewed=True,
        )
        assert result == []

    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.EntityMember")
    @pytest.mark.asyncio
    async def test_single_board_id(
        self, mock_entity_member, mock_content_type, mock_get_results_by_keys
    ):
        """A single-element list is handled correctly end-to-end."""
        mock_member = MagicMock()
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_filter = mock_entity_member.objects.select_related.return_value.filter
        mock_filter.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = [[mock_member]]

        result = await load_members_by_board_id([42])

        mock_filter.assert_called_once_with(
            entity_type=mock_content_type.objects.get_for_model.return_value,
            entity_id__in=[42],
            role=mock_entity_member.Role.MEMBER,
            is_active=True,
            is_reviewed=True,
        )
        assert result == [[mock_member]]

    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.board_of_directors.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.board_of_directors.EntityMember")
    @pytest.mark.asyncio
    async def test_uses_board_of_directors_content_type(
        self, mock_entity_member, mock_content_type, mock_get_results_by_keys
    ):
        """ContentType.objects.get_for_model is called with BoardOfDirectors."""
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_filter = mock_entity_member.objects.select_related.return_value.filter
        mock_filter.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = [[]]

        await load_members_by_board_id([1])

        mock_content_type.objects.get_for_model.assert_called_once_with(BoardOfDirectors)


class TestGetBoardOfDirectorsLoaders:
    """Tests for get_board_of_directors_loaders."""

    def test_returns_mapping(self):
        """Factory always returns a Mapping with both loaders."""
        loaders = get_board_of_directors_loaders()
        assert CANDIDATES_BY_BOARD_ID_LOADER in loaders
        assert MEMBERS_BY_BOARD_ID_LOADER in loaders
        assert isinstance(loaders[CANDIDATES_BY_BOARD_ID_LOADER], DataLoader)
        assert isinstance(loaders[MEMBERS_BY_BOARD_ID_LOADER], DataLoader)

    def test_returns_new_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_board_of_directors_loaders()
        loaders2 = get_board_of_directors_loaders()
        assert loaders1 is not loaders2
        assert (
            loaders1[CANDIDATES_BY_BOARD_ID_LOADER] is not loaders2[CANDIDATES_BY_BOARD_ID_LOADER]
        )
        assert loaders1[MEMBERS_BY_BOARD_ID_LOADER] is not loaders2[MEMBERS_BY_BOARD_ID_LOADER]

    def test_candidates_load_fn_is_load_candidates_by_board_id(self):
        """The candidates DataLoader is wired to load_candidates_by_board_id."""
        loaders = get_board_of_directors_loaders()
        assert loaders[CANDIDATES_BY_BOARD_ID_LOADER].load_fn is load_candidates_by_board_id

    def test_members_load_fn_is_load_members_by_board_id(self):
        """The members DataLoader is wired to load_members_by_board_id."""
        loaders = get_board_of_directors_loaders()
        assert loaders[MEMBERS_BY_BOARD_ID_LOADER].load_fn is load_members_by_board_id
