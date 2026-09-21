"""Tests for the board motion API."""

from http import HTTPStatus
from unittest.mock import MagicMock, patch

from django.db.models import F

from apps.api.rest.v0.board_motion import BoardMotionFilter, get_board_motion, list_board_motions


class TestListBoardMotions:
    """Tests for the list_board_motions endpoint."""

    @patch("apps.api.rest.v0.board_motion.BoardMotionModel")
    def test_list_motions_default_ordering(self, mock_motion_model):
        """Default ordering is by descending meeting date."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_motion_model.objects.select_related.return_value = mock_queryset
        mock_filters.filter.return_value = mock_queryset

        result = list_board_motions(mock_request, mock_filters, ordering=None)

        mock_queryset.order_by.assert_called_once_with(
            F("meeting_date").desc(nulls_last=True), "-id"
        )
        assert result == mock_queryset

    @patch("apps.api.rest.v0.board_motion.BoardMotionModel")
    def test_list_motions_with_ordering(self, mock_motion_model):
        """Custom ordering value is passed through to the queryset."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_motion_model.objects.select_related.return_value = mock_queryset
        mock_filters.filter.return_value = mock_queryset

        result = list_board_motions(mock_request, mock_filters, ordering="meeting_date")

        mock_queryset.order_by.assert_called_once_with(
            F("meeting_date").asc(nulls_last=True), "-id"
        )
        assert result == mock_queryset

    @patch("apps.api.rest.v0.board_motion.BoardMotionModel")
    def test_list_motions_applies_filters(self, mock_motion_model):
        """FilterSchema filters the motion queryset."""
        mock_request = MagicMock()
        mock_filters = BoardMotionFilter(sponsor=7)
        mock_queryset = MagicMock()
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_motion_model.objects.select_related.return_value = mock_queryset

        result = list_board_motions(mock_request, mock_filters, ordering=None)

        assert dict(mock_queryset.filter.call_args[0][0].children)["sponsor_id"] == 7
        assert result == mock_queryset


class TestGetBoardMotion:
    """Tests for the get_board_motion endpoint."""

    @patch("apps.api.rest.v0.board_motion.BoardMotionModel")
    def test_get_motion_success(self, mock_motion_model):
        """Return the matching motion when found."""
        mock_request = MagicMock()
        mock_motion = MagicMock()
        mock_qs = mock_motion_model.objects.annotate.return_value
        mock_qs = mock_qs.select_related.return_value
        mock_filtered_qs = mock_qs.filter.return_value
        mock_filtered_qs.first.return_value = mock_motion

        result = get_board_motion(mock_request, 1)

        mock_qs.filter.assert_called_once_with(id=1)
        assert result == mock_motion

    @patch("apps.api.rest.v0.board_motion.BoardMotionModel")
    def test_get_motion_not_found(self, mock_motion_model):
        """Return a 404 error response when the motion does not exist."""
        mock_request = MagicMock()
        mock_qs = mock_motion_model.objects.annotate.return_value
        mock_qs = mock_qs.select_related.return_value
        mock_filtered_qs = mock_qs.filter.return_value
        mock_filtered_qs.first.return_value = None

        result = get_board_motion(mock_request, 999)

        mock_qs.filter.assert_called_once_with(id=999)
        assert result.status_code == HTTPStatus.NOT_FOUND
