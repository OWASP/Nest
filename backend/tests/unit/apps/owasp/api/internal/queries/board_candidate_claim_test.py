"""Tests for BoardCandidateClaim GraphQL queries."""

from unittest.mock import MagicMock, patch

from apps.owasp.api.internal.queries.board_candidate_claim import BoardCandidateClaimQuery
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim


def _make_info(user):
    info = MagicMock()
    info.context.request.user = user
    return info


class TestBoardCandidateClaimQuery:
    """Tests for board_candidate_claims query."""

    @patch("apps.owasp.api.internal.queries.board_candidate_claim.BoardCandidateClaim")
    def test_board_candidate_claims_self(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = MagicMock()
        user.github_user.login = "alice"
        info = _make_info(user)

        claims = [MagicMock(), MagicMock()]
        mock_qs = MagicMock()
        mock_qs.order_by.return_value = claims
        mock_claim_model.objects.filter.return_value = mock_qs

        query = BoardCandidateClaimQuery()
        result = query.board_candidate_claims(info, login="alice", year=2025)

        mock_claim_model.objects.filter.assert_called_once_with(
            candidate__member__login="alice",
            board__year=2025,
        )
        assert result == claims

    @patch("apps.owasp.api.internal.queries.board_candidate_claim.BoardCandidateClaim")
    def test_board_candidate_claims_non_self_filters_approved(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = MagicMock()
        user.github_user.login = "bob"
        info = _make_info(user)

        base_qs = MagicMock()
        ordered_qs = MagicMock()
        filtered_qs = MagicMock()
        ordered_qs.filter.return_value = filtered_qs
        base_qs.order_by.return_value = ordered_qs
        mock_claim_model.objects.filter.return_value = base_qs

        query = BoardCandidateClaimQuery()
        result = query.board_candidate_claims(info, login="alice", year=2025)

        ordered_qs.filter.assert_called_once_with(status=BoardCandidateClaim.Status.APPROVED)
        assert result == filtered_qs

    @patch("apps.owasp.api.internal.queries.board_candidate_claim.BoardCandidateClaim")
    def test_board_candidate_claims_anonymous_filters_approved(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = False
        info = _make_info(user)

        base_qs = MagicMock()
        ordered_qs = MagicMock()
        filtered_qs = MagicMock()
        ordered_qs.filter.return_value = filtered_qs
        base_qs.order_by.return_value = ordered_qs
        mock_claim_model.objects.filter.return_value = base_qs

        query = BoardCandidateClaimQuery()
        result = query.board_candidate_claims(info, login="alice", year=2025)

        ordered_qs.filter.assert_called_once_with(status=BoardCandidateClaim.Status.APPROVED)
        assert result == filtered_qs
