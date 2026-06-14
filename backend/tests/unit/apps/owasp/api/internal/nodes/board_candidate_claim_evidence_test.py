"""Tests for BoardCandidateClaimEvidence GraphQL node."""

from apps.owasp.api.internal.nodes.board_candidate_claim_evidence import (
    BoardCandidateClaimEvidenceNode,
)
from tests.unit.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestBoardCandidateClaimEvidenceNode(GraphQLNodeBaseTest):
    """Test cases for BoardCandidateClaimEvidenceNode class."""

    def test_node_fields(self):
        field_names = {
            field.name
            for field in BoardCandidateClaimEvidenceNode.__strawberry_definition__.fields
        }
        expected_field_names = {
            "_id",
            "created_at",
            "description",
            "has_file",
            "key",
            "name",
            "source_url",
            "updated_at",
        }
        assert field_names == expected_field_names
