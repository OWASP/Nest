"""Tests for BoardCandidateClaimReview GraphQL node."""

from unittest.mock import Mock

from apps.owasp.api.internal.nodes.board_candidate_claim_review import (
    BoardCandidateClaimReviewNode,
)
from apps.owasp.api.internal.nodes.enum import ReviewStatusEnum
from tests.unit.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestBoardCandidateClaimReviewNode(GraphQLNodeBaseTest):
    """Test cases for BoardCandidateClaimReviewNode class."""

    def test_node_fields(self):
        """Test node fields."""
        field_names = {
            field.name for field in BoardCandidateClaimReviewNode.__strawberry_definition__.fields
        }
        expected_field_names = {
            "_id",
            "created_at",
            "notes",
            "reviewer",
            "status",
        }
        assert field_names == expected_field_names

    def test_created_at(self):
        """Test created_at resolver."""
        mock_review = Mock()
        mock_review.nest_created_at = Mock()

        field = self._get_field_by_name("created_at", BoardCandidateClaimReviewNode)
        result = field.base_resolver.wrapped_func(None, mock_review)

        assert result == mock_review.nest_created_at

    def test_reviewer(self):
        """Test reviewer resolver."""
        mock_review = Mock()
        mock_review.reviewer.github_user = Mock()

        field = self._get_field_by_name("reviewer", BoardCandidateClaimReviewNode)
        result = field.base_resolver.wrapped_func(None, mock_review)

        assert result == mock_review.reviewer.github_user

    def test_status(self):
        """Test status resolver."""
        mock_review = Mock()
        mock_review.status = ReviewStatusEnum.APPROVED.value

        field = self._get_field_by_name("status", BoardCandidateClaimReviewNode)
        result = field.base_resolver.wrapped_func(None, mock_review)

        assert result == ReviewStatusEnum.APPROVED
