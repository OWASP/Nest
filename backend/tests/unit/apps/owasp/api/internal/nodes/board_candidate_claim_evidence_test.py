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
            "file_name",
            "file_size",
            "file_url",
            "is_removed",
            "key",
            "name",
            "removed_at",
            "removed_reason",
            "source_url",
            "updated_at",
        }
        assert field_names == expected_field_names

    def test_file_url_resolver(self):
        """Test file_url returns URL from evidence instance."""
        mock_evidence = Mock()
        mock_file = Mock()
        mock_file.url = "/media/bod/claim/evidence/test.pdf"
        mock_evidence.file = mock_file

        field = self._get_field_by_name("file_url", BoardCandidateClaimEvidenceNode)
        result = field.base_resolver.wrapped_func(mock_evidence)

        assert result == "/media/bod/claim/evidence/test.pdf"

    def test_file_url_returns_none_when_no_file(self):
        """Test file_url returns None when evidence has no file."""
        mock_evidence = Mock()
        mock_evidence.file = None

        field = self._get_field_by_name("file_url", BoardCandidateClaimEvidenceNode)
        result = field.base_resolver.wrapped_func(mock_evidence)

        assert result is None
