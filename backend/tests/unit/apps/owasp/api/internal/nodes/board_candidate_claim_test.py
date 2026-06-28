"""Tests for BoardCandidateClaim GraphQL node."""

from unittest.mock import MagicMock, Mock

from apps.owasp.api.internal.nodes.board_candidate_claim import BoardCandidateClaimNode
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from tests.unit.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestBoardCandidateClaimNode(GraphQLNodeBaseTest):
    """Test cases for BoardCandidateClaimNode class."""

    def _make_info(self, user):
        info = MagicMock()
        info.context.request.user = user
        return info

    def test_node_fields(self):
        field_names = {
            field.name for field in BoardCandidateClaimNode.__strawberry_definition__.fields
        }
        expected_field_names = {
            "_id",
            "created_at",
            "description",
            "is_locked",
            "key",
            "name",
            "order",
            "reviews",
            "status",
            "updated_at",
            "withdrawn_at",
            "withdrawn_reason",
        }
        assert field_names == expected_field_names

    def test_reviews_self_sees_all(self):
        mock_github_user = Mock()
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = mock_github_user
        info = self._make_info(user)

        mock_claim = Mock()
        mock_claim.candidate.member = mock_github_user
        mock_claim.status = BoardCandidateClaim.Status.DRAFT
        mock_queryset = MagicMock()
        mock_claim.reviews = MagicMock()
        mock_claim.reviews.all.return_value = mock_queryset

        field = self._get_field_by_name("reviews", BoardCandidateClaimNode)
        result = field.base_resolver.wrapped_func(None, mock_claim, info)

        mock_claim.reviews.all.assert_called_once()
        assert result == mock_queryset

    def test_reviews_approved_sees_all(self):
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = Mock()
        info = self._make_info(user)

        mock_claim = Mock()
        mock_claim.candidate.member = Mock()
        mock_claim.status = BoardCandidateClaim.Status.APPROVED
        mock_queryset = MagicMock()
        mock_claim.reviews = MagicMock()
        mock_claim.reviews.all.return_value = mock_queryset

        field = self._get_field_by_name("reviews", BoardCandidateClaimNode)
        result = field.base_resolver.wrapped_func(None, mock_claim, info)

        mock_claim.reviews.all.assert_called_once()
        assert result == mock_queryset

    def test_reviews_reviewer_sees_own(self):
        mock_github_user = Mock()
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = mock_github_user
        user.github_user.is_owasp_staff = True
        user.github_user.is_claim_reviewer = False
        info = self._make_info(user)

        mock_claim = Mock()
        mock_claim.candidate.member = Mock()
        mock_claim.status = BoardCandidateClaim.Status.SUBMITTED
        mock_queryset = MagicMock()
        mock_claim.reviews = MagicMock()
        mock_claim.reviews.filter.return_value = mock_queryset

        field = self._get_field_by_name("reviews", BoardCandidateClaimNode)
        result = field.base_resolver.wrapped_func(None, mock_claim, info)

        mock_claim.reviews.filter.assert_called_once_with(reviewer=mock_github_user)
        assert result == mock_queryset

    def test_reviews_non_reviewer_gets_empty_on_submitted(self):
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = Mock()
        user.github_user = mock_github_user
        mock_github_user.is_owasp_staff = False
        mock_github_user.is_claim_reviewer = False
        info = self._make_info(user)

        mock_claim = Mock()
        mock_claim.candidate.member = Mock()
        mock_claim.status = BoardCandidateClaim.Status.SUBMITTED

        field = self._get_field_by_name("reviews", BoardCandidateClaimNode)
        result = field.base_resolver.wrapped_func(None, mock_claim, info)

        assert result == []

    def test_reviews_anonymous_gets_empty_on_submitted(self):
        user = MagicMock()
        user.is_authenticated = False
        info = self._make_info(user)

        mock_claim = Mock()
        mock_claim.status = BoardCandidateClaim.Status.SUBMITTED

        field = self._get_field_by_name("reviews", BoardCandidateClaimNode)
        result = field.base_resolver.wrapped_func(None, mock_claim, info)

        assert result == []
