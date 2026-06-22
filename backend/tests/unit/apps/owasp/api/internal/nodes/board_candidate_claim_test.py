"""Tests for BoardCandidateClaim GraphQL node."""

from unittest.mock import Mock

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
            "created_at",
            "description",
            "has_evidence",
            "is_locked",
            "key",
            "name",
            "order",
            "status",
            "updated_at",
            "withdrawn_at",
            "withdrawn_reason",
        }
        assert field_names == expected_field_names

    def test_has_evidence_returns_true_when_evidence_exists(self):
        mock_claim = Mock()
        mock_claim.evidence_exists = True

        field = self._get_field_by_name("has_evidence", BoardCandidateClaimNode)
        result = field.base_resolver.wrapped_func(None, mock_claim)

        assert result

    def test_has_evidence_returns_false_when_no_evidence(self):
        mock_claim = Mock()
        mock_claim.evidence_exists = False

        field = self._get_field_by_name("has_evidence", BoardCandidateClaimNode)
        result = field.base_resolver.wrapped_func(None, mock_claim)

        assert not result

    def test_has_evidence_falls_back_to_evidences_filter_when_annotation_missing(self):
        mock_claim = Mock(spec=[])
        mock_claim.evidences = Mock()
        mock_claim.evidences.filter.return_value.exists.return_value = True

        field = self._get_field_by_name("has_evidence", BoardCandidateClaimNode)
        result = field.base_resolver.wrapped_func(None, mock_claim)

        mock_claim.evidences.filter.assert_called_once_with(is_removed=False)
        assert result
