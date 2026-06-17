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


class TestBoardCandidateClaimSingleQuery:
    """Tests for board_candidate_claim single claim query."""

    @patch("apps.owasp.api.internal.queries.board_candidate_claim.BoardCandidateClaim")
    def test_board_candidate_claim_self(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        mock_claim_model.DoesNotExist = BoardCandidateClaim.DoesNotExist
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)

        claim = MagicMock()
        claim.candidate.member = mock_github_user
        claim.status = BoardCandidateClaim.Status.DRAFT
        mock_claim_model.objects.get.return_value = claim

        query = BoardCandidateClaimQuery()
        result = query.board_candidate_claim(info, login="alice", key="test-key", year=2025)

        mock_claim_model.objects.get.assert_called_once_with(
            candidate__member__login="alice", key="test-key", board__year=2025
        )
        assert result == claim

    @patch("apps.owasp.api.internal.queries.board_candidate_claim.BoardCandidateClaim")
    def test_board_candidate_claim_non_self_approved(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        mock_claim_model.DoesNotExist = BoardCandidateClaim.DoesNotExist
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = MagicMock()
        info = _make_info(user)

        claim = MagicMock()
        claim.candidate.member = MagicMock()
        claim.status = BoardCandidateClaim.Status.APPROVED
        mock_claim_model.objects.get.return_value = claim

        query = BoardCandidateClaimQuery()
        result = query.board_candidate_claim(info, login="alice", key="test-key", year=2025)

        assert result == claim

    @patch("apps.owasp.api.internal.queries.board_candidate_claim.BoardCandidateClaim")
    def test_board_candidate_claim_non_self_not_approved(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        mock_claim_model.DoesNotExist = BoardCandidateClaim.DoesNotExist
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = MagicMock()
        info = _make_info(user)

        claim = MagicMock()
        claim.candidate.member = MagicMock()
        claim.status = BoardCandidateClaim.Status.SUBMITTED
        mock_claim_model.objects.get.return_value = claim

        query = BoardCandidateClaimQuery()
        result = query.board_candidate_claim(info, login="alice", key="test-key", year=2025)

        assert result is None

    @patch("apps.owasp.api.internal.queries.board_candidate_claim.BoardCandidateClaim")
    def test_board_candidate_claim_not_found(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        mock_claim_model.DoesNotExist = BoardCandidateClaim.DoesNotExist
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = MagicMock()
        info = _make_info(user)

        mock_claim_model.objects.get.side_effect = BoardCandidateClaim.DoesNotExist

        query = BoardCandidateClaimQuery()
        result = query.board_candidate_claim(info, login="alice", key="test-key", year=2025)

        assert result is None

    @patch("apps.owasp.api.internal.queries.board_candidate_claim.BoardCandidateClaim")
    def test_board_candidate_claim_anonymous_approved(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        mock_claim_model.DoesNotExist = BoardCandidateClaim.DoesNotExist
        user = MagicMock()
        user.is_authenticated = False
        info = _make_info(user)

        claim = MagicMock()
        claim.status = BoardCandidateClaim.Status.APPROVED
        mock_claim_model.objects.get.return_value = claim

        query = BoardCandidateClaimQuery()
        result = query.board_candidate_claim(info, login="alice", key="test-key", year=2025)

        assert result == claim
