"""Tests for BoardOfDirectors GraphQL queries."""

from unittest.mock import Mock, patch

from apps.owasp.api.internal.queries.board_of_directors import BoardOfDirectorsQuery


class TestBoardOfDirectorsQuery:
    def test_board_of_directors_found(self):
        query = BoardOfDirectorsQuery()

        mock_board = Mock()
        mock_board.year = 2025

        with patch(
            "apps.owasp.api.internal.queries.board_of_directors.BoardOfDirectors"
        ) as mock_board_cls:
            mock_board_cls.objects.get.return_value = mock_board

            result = query.board_of_directors(year=2025)

            mock_board_cls.objects.get.assert_called_once_with(year=2025)
            assert result == mock_board

    def test_board_of_directors_not_found(self):
        from apps.owasp.models.board_of_directors import BoardOfDirectors

        query = BoardOfDirectorsQuery()

        with patch(
            "apps.owasp.api.internal.queries.board_of_directors.BoardOfDirectors.objects.get"
        ) as mock_get:
            mock_get.side_effect = BoardOfDirectors.DoesNotExist

            result = query.board_of_directors(year=2099)

            assert result is None

    def test_boards_of_directors_all(self):
        query = BoardOfDirectorsQuery()

        mock_boards = [Mock(year=2025), Mock(year=2024)]

        with patch(
            "apps.owasp.api.internal.queries.board_of_directors.BoardOfDirectors"
        ) as mock_board_cls:
            mock_queryset = Mock()
            mock_queryset.order_by.return_value = mock_queryset
            mock_queryset.__getitem__ = Mock(return_value=mock_boards)

            mock_board_cls.objects.order_by.return_value = mock_queryset

            result = query.boards_of_directors(limit=10)

            mock_board_cls.objects.order_by.assert_called_once_with("-year")
            mock_queryset.__getitem__.assert_called_once_with(slice(None, 10, None))
            assert result == mock_boards

    def test_boards_of_directors_with_custom_limit(self):
        query = BoardOfDirectorsQuery()

        mock_boards = [Mock(year=2025)]

        with patch(
            "apps.owasp.api.internal.queries.board_of_directors.BoardOfDirectors"
        ) as mock_board_cls:
            mock_queryset = Mock()
            mock_queryset.order_by.return_value = mock_queryset
            mock_queryset.__getitem__ = Mock(return_value=mock_boards)

            mock_board_cls.objects.order_by.return_value = mock_queryset

            result = query.boards_of_directors(limit=5)

            mock_queryset.__getitem__.assert_called_once_with(slice(None, 5, None))
            assert result == mock_boards

    def test_boards_of_directors_with_invalid_limit(self):
        """Test boards_of_directors returns empty list for invalid limit."""
        query = BoardOfDirectorsQuery()

        result = query.boards_of_directors(limit=0)
        assert result == []

        result = query.boards_of_directors(limit=-1)
        assert result == []
