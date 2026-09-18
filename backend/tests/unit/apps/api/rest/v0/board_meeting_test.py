"""Tests for the board meeting API."""

from http import HTTPStatus
from unittest.mock import MagicMock, patch

from apps.api.rest.v0.board_meeting import (
    BoardMeetingFilter,
    get_board_meeting,
    list_board_meetings,
)


class TestListBoardMeetings:
    """Tests for the list_board_meetings endpoint."""

    @patch("apps.api.rest.v0.board_meeting.BoardMeetingModel")
    def test_list_meetings_default_ordering(self, mock_meeting_model):
        """Default ordering is by descending meeting date."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_meeting_model.objects.order_by.return_value = mock_queryset
        mock_filters.filter.return_value = mock_queryset

        result = list_board_meetings(mock_request, mock_filters, ordering=None)

        mock_meeting_model.objects.order_by.assert_called_once_with("-date", "-id")
        assert result == mock_queryset

    @patch("apps.api.rest.v0.board_meeting.BoardMeetingModel")
    def test_list_meetings_with_ordering(self, mock_meeting_model):
        """Custom ordering value is passed through to the queryset."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_meeting_model.objects.order_by.return_value = mock_queryset
        mock_filters.filter.return_value = mock_queryset

        result = list_board_meetings(mock_request, mock_filters, ordering="date")

        mock_meeting_model.objects.order_by.assert_called_once_with("date", "-id")
        assert result == mock_queryset

    @patch("apps.api.rest.v0.board_meeting.BoardMeetingModel")
    def test_list_meetings_applies_filters(self, mock_meeting_model):
        """FilterSchema filters the meeting queryset."""
        mock_request = MagicMock()
        mock_filters = BoardMeetingFilter(type="public")
        mock_queryset = MagicMock()
        mock_meeting_model.objects.order_by.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset

        result = list_board_meetings(mock_request, mock_filters, ordering=None)

        mock_queryset.filter.assert_called_once()
        assert result == mock_queryset


class TestGetBoardMeeting:
    """Tests for the get_board_meeting endpoint."""

    @patch("apps.api.rest.v0.board_meeting.BoardMeetingModel")
    def test_get_meeting_success(self, mock_meeting_model):
        """Return the matching meeting when found."""
        mock_request = MagicMock()
        mock_meeting = MagicMock()
        mock_qs = mock_meeting_model.objects.select_related.return_value
        mock_qs = mock_qs.prefetch_related.return_value
        mock_qs = mock_qs.filter.return_value
        mock_qs.first.return_value = mock_meeting

        result = get_board_meeting(mock_request, 1)

        assert result == mock_meeting

    @patch("apps.api.rest.v0.board_meeting.BoardMeetingModel")
    def test_get_meeting_not_found(self, mock_meeting_model):
        """Return a 404 error response when the meeting does not exist."""
        mock_request = MagicMock()
        mock_qs = mock_meeting_model.objects.select_related.return_value
        mock_qs = mock_qs.prefetch_related.return_value
        mock_qs = mock_qs.filter.return_value
        mock_qs.first.return_value = None

        result = get_board_meeting(mock_request, 999)

        assert result.status_code == HTTPStatus.NOT_FOUND
