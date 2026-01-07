"""Tests for BoardOfDirectors GraphQL node."""

from unittest.mock import Mock

from apps.owasp.api.internal.nodes.board_of_directors import BoardOfDirectorsNode


class TestBoardOfDirectorsNode:
    """Test cases for BoardOfDirectorsNode class."""

    def _get_field_by_name(self, name):
        return next(
            (f for f in BoardOfDirectorsNode.__strawberry_definition__.fields if f.name == name),
            None,
        )

    def test_node_fields(self):
        field_names = {
            field.name for field in BoardOfDirectorsNode.__strawberry_definition__.fields
        }
        expected_field_names = {
            "year",
            "created_at",
            "updated_at",
            "owasp_url",
            "candidates",
            "members",
            "_id",
        }
        assert field_names == expected_field_names

    def test_owasp_url_resolver(self):
        """Test owasp_url returns URL from board instance."""
        mock_board = Mock()
        mock_board.owasp_url = "https://board.owasp.org/elections/2025_elections"

        field = self._get_field_by_name("owasp_url")
        resolver = field.base_resolver.wrapped_func
        result = resolver(mock_board)

        assert result == "https://board.owasp.org/elections/2025_elections"

    def test_candidates_resolver(self):
        """Test candidates returns list from get_candidates method."""
        mock_candidate1 = Mock()
        mock_candidate2 = Mock()

        mock_board = Mock()
        mock_board.get_candidates.return_value = [mock_candidate1, mock_candidate2]

        field = self._get_field_by_name("candidates")
        resolver = field.base_resolver.wrapped_func
        result = resolver(mock_board)

        assert result == [mock_candidate1, mock_candidate2]
        mock_board.get_candidates.assert_called_once()

    def test_members_resolver(self):
        """Test members returns list from get_members method."""
        mock_member1 = Mock()
        mock_member2 = Mock()

        mock_board = Mock()
        mock_board.get_members.return_value = [mock_member1, mock_member2]

        field = self._get_field_by_name("members")
        resolver = field.base_resolver.wrapped_func
        result = resolver(mock_board)

        assert result == [mock_member1, mock_member2]
        mock_board.get_members.assert_called_once()
