"""Tests for the board outcome API."""

from datetime import UTC, datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
from django.db.models import F

from apps.api.rest.v0.board_outcome import (
    BoardOutcomeFilter,
    get_board_outcome,
    list_board_outcomes,
)


class TestListBoardOutcomes:
    """Tests for the list_board_outcomes endpoint."""

    @patch("apps.api.rest.v0.board_outcome.BoardOutcomeModel")
    def test_list_outcomes_default_ordering(self, mock_outcome_model):
        """Default ordering is by descending meeting date."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_outcome_model.objects.all.return_value = mock_queryset
        mock_filters.filter.return_value = mock_queryset

        result = list_board_outcomes(mock_request, mock_filters, ordering=None)

        mock_queryset.order_by.assert_called_once_with(
            F("meeting_date").desc(nulls_last=True), "-id"
        )
        assert result == mock_queryset

    @pytest.mark.parametrize(
        ("ordering", "field", "descending"),
        [
            ("due_date", "due_date", False),
            ("-due_date", "due_date", True),
            ("meeting_date", "meeting_date", False),
            ("-meeting_date", "meeting_date", True),
        ],
    )
    @patch("apps.api.rest.v0.board_outcome.BoardOutcomeModel")
    def test_list_outcomes_ordering(self, mock_outcome_model, ordering, field, descending):
        """Each supported ordering maps to its nullable-aware column ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_outcome_model.objects.all.return_value = mock_queryset
        mock_filters.filter.return_value = mock_queryset

        result = list_board_outcomes(mock_request, mock_filters, ordering=ordering)

        expected = F(field).desc(nulls_last=True) if descending else F(field).asc(nulls_last=True)
        mock_queryset.order_by.assert_called_once_with(expected, "-id")
        assert result == mock_queryset

    @patch("apps.api.rest.v0.board_outcome.BoardOutcomeModel")
    def test_list_outcomes_applies_filters(self, mock_outcome_model):
        """FilterSchema filters the outcome queryset."""
        mock_request = MagicMock()
        mock_filters = BoardOutcomeFilter(status="pending", assignee=1)
        mock_queryset = MagicMock()
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_outcome_model.objects.all.return_value = mock_queryset

        result = list_board_outcomes(mock_request, mock_filters, ordering=None)

        assert dict(mock_queryset.filter.call_args[0][0].children) == {
            "assignees__id": 1,
            "status": "pending",
        }
        assert result == mock_queryset

    @patch("apps.api.rest.v0.board_outcome.BoardOutcomeModel")
    def test_list_outcomes_normalizes_date_filters(self, mock_outcome_model):
        """Extreme offsets in date filters are normalized before reaching the ORM."""
        mock_request = MagicMock()
        mock_filters = BoardOutcomeFilter(
            date_gte="1447-05-09T03:57:07.246491-22:14",
            date_lte="8292-12-23T16:24:08.050762+21:14",
        )
        mock_queryset = MagicMock()
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_outcome_model.objects.all.return_value = mock_queryset

        result = list_board_outcomes(mock_request, mock_filters, ordering=None)

        children = dict(mock_queryset.filter.call_args[0][0].children)
        assert children["meeting_date__gte"] == datetime(1447, 5, 10, 2, 11, 7, 246491, tzinfo=UTC)
        assert children["meeting_date__lte"] == datetime(
            8292, 12, 22, 19, 10, 8, 50762, tzinfo=UTC
        )
        assert result == mock_queryset


class TestGetBoardOutcome:
    """Tests for the get_board_outcome endpoint."""

    @patch("apps.api.rest.v0.board_outcome.BoardOutcomeModel")
    def test_get_outcome_success(self, mock_outcome_model):
        """Return the matching outcome when found."""
        mock_request = MagicMock()
        mock_outcome = MagicMock()
        mock_qs = mock_outcome_model.objects.annotate.return_value
        mock_prefetched_qs = mock_qs.prefetch_related.return_value
        mock_filtered_qs = mock_prefetched_qs.filter.return_value
        mock_filtered_qs.first.return_value = mock_outcome

        result = get_board_outcome(mock_request, 1)

        mock_prefetched_qs.filter.assert_called_once_with(id=1)
        assert result == mock_outcome

    @patch("apps.api.rest.v0.board_outcome.BoardOutcomeModel")
    def test_get_outcome_not_found(self, mock_outcome_model):
        """Return a 404 error response when the outcome does not exist."""
        mock_request = MagicMock()
        mock_qs = mock_outcome_model.objects.annotate.return_value
        mock_prefetched_qs = mock_qs.prefetch_related.return_value
        mock_filtered_qs = mock_prefetched_qs.filter.return_value
        mock_filtered_qs.first.return_value = None

        result = get_board_outcome(mock_request, 999)

        mock_prefetched_qs.filter.assert_called_once_with(id=999)
        assert result.status_code == HTTPStatus.NOT_FOUND
