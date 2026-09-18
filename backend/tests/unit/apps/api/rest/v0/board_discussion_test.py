"""Tests for the board discussion API."""

from datetime import UTC, datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch

from apps.api.rest.v0.board_discussion import (
    BoardDiscussionFilter,
    get_board_discussion,
    list_board_discussions,
)


class TestListBoardDiscussions:
    """Tests for the list_board_discussions endpoint."""

    @patch("apps.api.rest.v0.board_discussion.BoardDiscussionModel")
    def test_list_discussions_default_ordering(self, mock_discussion_model):
        """Default ordering is by descending meeting date."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_discussion_model.objects.all.return_value = mock_queryset
        mock_filters.filter.return_value = mock_queryset

        result = list_board_discussions(mock_request, mock_filters, ordering=None)

        mock_queryset.order_by.assert_called_once_with("-meeting_date", "-id")
        assert result == mock_queryset

    @patch("apps.api.rest.v0.board_discussion.BoardDiscussionModel")
    def test_list_discussions_with_ordering(self, mock_discussion_model):
        """Custom ordering value is passed through to the queryset."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_discussion_model.objects.all.return_value = mock_queryset
        mock_filters.filter.return_value = mock_queryset

        result = list_board_discussions(mock_request, mock_filters, ordering="meeting_date")

        mock_queryset.order_by.assert_called_once_with("meeting_date", "-id")
        assert result == mock_queryset

    @patch("apps.api.rest.v0.board_discussion.BoardDiscussionModel")
    def test_list_discussions_applies_filters(self, mock_discussion_model):
        """FilterSchema filters the discussion queryset."""
        mock_request = MagicMock()
        date_gte = datetime(2024, 1, 1, tzinfo=UTC)
        mock_filters = BoardDiscussionFilter(date_gte=date_gte)
        mock_queryset = MagicMock()
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_discussion_model.objects.all.return_value = mock_queryset

        result = list_board_discussions(mock_request, mock_filters, ordering=None)

        mock_queryset.filter.assert_called_once()
        assert dict(mock_queryset.filter.call_args[0][0].children)["meeting_date__gte"] == date_gte
        assert result == mock_queryset


class TestGetBoardDiscussion:
    """Tests for the get_board_discussion endpoint."""

    @patch("apps.api.rest.v0.board_discussion.BoardDiscussionModel")
    def test_get_discussion_success(self, mock_discussion_model):
        """Return the matching discussion when found."""
        mock_request = MagicMock()
        mock_discussion = MagicMock()
        mock_qs = mock_discussion_model.objects.annotate.return_value
        mock_qs = mock_qs.prefetch_related.return_value
        mock_filtered_qs = mock_qs.filter.return_value
        mock_filtered_qs.first.return_value = mock_discussion

        result = get_board_discussion(mock_request, 1)

        mock_qs.filter.assert_called_once_with(id=1)
        assert result == mock_discussion

    @patch("apps.api.rest.v0.board_discussion.BoardDiscussionModel")
    def test_get_discussion_not_found(self, mock_discussion_model):
        """Return a 404 error response when the discussion does not exist."""
        mock_request = MagicMock()
        mock_qs = mock_discussion_model.objects.annotate.return_value
        mock_prefetched_qs = mock_qs.prefetch_related.return_value
        mock_filtered_qs = mock_prefetched_qs.filter.return_value
        mock_filtered_qs.first.return_value = None

        result = get_board_discussion(mock_request, 999)

        mock_prefetched_qs.filter.assert_called_once_with(id=999)
        assert result.status_code == HTTPStatus.NOT_FOUND
