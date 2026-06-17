"""Tests for BoardCandidateClaimEvidence GraphQL node."""

from unittest.mock import Mock

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

    def test_has_file_returns_true_when_file_exists(self):
        mock_evidence = Mock()
        mock_evidence.file = Mock()

        field = self._get_field_by_name("has_file", BoardCandidateClaimEvidenceNode)
        result = field.base_resolver.wrapped_func(None, mock_evidence)

        assert result is True

    def test_has_file_returns_false_when_file_is_none(self):
        mock_evidence = Mock()
        mock_evidence.file = None

        field = self._get_field_by_name("has_file", BoardCandidateClaimEvidenceNode)
        result = field.base_resolver.wrapped_func(None, mock_evidence)

        assert result is False
