"""Tests for the board vote API."""

from http import HTTPStatus
from unittest.mock import MagicMock, patch

from apps.api.rest.v0.board_vote import BoardVoteFilter, get_board_vote, list_board_votes


class TestListBoardVotes:
    """Tests for the list_board_votes endpoint."""

    @patch("apps.api.rest.v0.board_vote.BoardVoteModel")
    def test_list_votes_default_ordering(self, mock_vote_model):
        """Default ordering is by descending meeting date."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_vote_model.objects.all.return_value = mock_queryset
        mock_filters.filter.return_value = mock_queryset

        result = list_board_votes(mock_request, mock_filters, ordering=None)

        mock_queryset.order_by.assert_called_once_with("-meeting_date", "-id")
        assert result == mock_queryset

    @patch("apps.api.rest.v0.board_vote.BoardVoteModel")
    def test_list_votes_with_ordering(self, mock_vote_model):
        """Custom ordering value is passed through to the queryset."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_vote_model.objects.all.return_value = mock_queryset
        mock_filters.filter.return_value = mock_queryset

        result = list_board_votes(mock_request, mock_filters, ordering="meeting_date")

        mock_queryset.order_by.assert_called_once_with("meeting_date", "-id")
        assert result == mock_queryset

    @patch("apps.api.rest.v0.board_vote.BoardVoteModel")
    def test_list_votes_applies_filters(self, mock_vote_model):
        """FilterSchema filters the vote queryset."""
        mock_request = MagicMock()
        mock_filters = BoardVoteFilter(result="passed", type="vote", motion_id=5)
        mock_queryset = MagicMock()
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_vote_model.objects.all.return_value = mock_queryset

        result = list_board_votes(mock_request, mock_filters, ordering=None)

        mock_queryset.filter.assert_called_once()
        assert result == mock_queryset


class TestGetBoardVote:
    """Tests for the get_board_vote endpoint."""

    @patch("apps.api.rest.v0.board_vote.BoardVoteModel")
    def test_get_vote_success(self, mock_vote_model):
        """Return the matching vote when found."""
        mock_request = MagicMock()
        mock_vote = MagicMock()
        mock_qs = mock_vote_model.objects.annotate.return_value
        mock_qs = mock_qs.prefetch_related.return_value
        mock_qs = mock_qs.filter.return_value
        mock_qs.first.return_value = mock_vote

        result = get_board_vote(mock_request, 1)

        assert result == mock_vote

    @patch("apps.api.rest.v0.board_vote.BoardVoteModel")
    def test_get_vote_not_found(self, mock_vote_model):
        """Return a 404 error response when the vote does not exist."""
        mock_request = MagicMock()
        mock_qs = mock_vote_model.objects.annotate.return_value
        mock_qs = mock_qs.prefetch_related.return_value
        mock_qs = mock_qs.filter.return_value
        mock_qs.first.return_value = None

        result = get_board_vote(mock_request, 999)

        assert result.status_code == HTTPStatus.NOT_FOUND
