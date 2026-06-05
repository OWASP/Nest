"""Tests for BoardCandidateClaim GraphQL node."""

from apps.owasp.api.internal.nodes.board_candidate_claim import BoardCandidateClaimNode
from tests.unit.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestBoardCandidateClaimNode(GraphQLNodeBaseTest):
    """Test cases for BoardCandidateClaimNode class."""

    def test_node_fields(self):
        field_names = {
            field.name for field in BoardCandidateClaimNode.__strawberry_definition__.fields
        }
        expected_field_names = {
            "_id",
            "description",
            "is_locked",
            "nest_created_at",
            "nest_updated_at",
            "order",
            "status",
            "title",
            "withdrawn_at",
            "withdrawn_reason",
        }
        assert field_names == expected_field_names
