"""Tests for BoardOfDirectors GraphQL node."""

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
