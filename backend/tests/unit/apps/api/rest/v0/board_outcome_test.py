"""Tests for the board outcome API."""

from http import HTTPStatus
from unittest.mock import MagicMock, patch

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

        mock_queryset.order_by.assert_called_once_with("-meeting_date", "-id")
        assert result == mock_queryset

    @patch("apps.api.rest.v0.board_outcome.BoardOutcomeModel")
    def test_list_outcomes_due_date_ordering(self, mock_outcome_model):
        """Due date ordering maps directly to the due_date column."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_outcome_model.objects.all.return_value = mock_queryset
        mock_filters.filter.return_value = mock_queryset

        result = list_board_outcomes(mock_request, mock_filters, ordering="due_date")

        mock_queryset.order_by.assert_called_once_with("due_date", "-id")
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
