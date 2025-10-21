"""Tests for BoardOfDirectors GraphQL node."""

from unittest.mock import Mock

from apps.owasp.api.internal.nodes.board_of_directors import BoardOfDirectorsNode


class TestBoardOfDirectorsNode:
    def test_node_fields(self):
        node = BoardOfDirectorsNode.__strawberry_definition__

        field_names = {field.name for field in node.fields}

        assert "year" in field_names
        assert "created_at" in field_names
        assert "updated_at" in field_names
        assert "owasp_url" in field_names
        assert "candidates" in field_names
        assert "members" in field_names

    def test_owasp_url_resolver(self):
        """Test owasp_url returns URL from board instance."""
        mock_board = Mock()
        mock_board.owasp_url = "https://board.owasp.org/elections/2025_elections"

        result = BoardOfDirectorsNode.owasp_url(mock_board)

        assert result == "https://board.owasp.org/elections/2025_elections"

    def test_candidates_resolver(self):
        """Test candidates returns list from get_candidates method."""
        mock_candidate1 = Mock()
        mock_candidate2 = Mock()

        mock_board = Mock()
        mock_board.get_candidates.return_value = [mock_candidate1, mock_candidate2]

        result = BoardOfDirectorsNode.candidates(mock_board)

        assert result == [mock_candidate1, mock_candidate2]
        mock_board.get_candidates.assert_called_once()

    def test_members_resolver(self):
        """Test members returns list from get_members method."""
        mock_member1 = Mock()
        mock_member2 = Mock()

        mock_board = Mock()
        mock_board.get_members.return_value = [mock_member1, mock_member2]

        result = BoardOfDirectorsNode.members(mock_board)

        assert result == [mock_member1, mock_member2]
        mock_board.get_members.assert_called_once()
