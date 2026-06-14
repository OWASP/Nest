"""Tests for BoardCandidateClaimEvidence GraphQL queries."""

from unittest.mock import MagicMock, patch

from apps.owasp.api.internal.queries.board_candidate_claim_evidence import (
    BoardCandidateClaimEvidenceQuery,
)
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim


def _make_info(user):
    info = MagicMock()
    info.context.request.user = user
    return info


class TestBoardCandidateClaimEvidenceQuery:
    """Tests for board_candidate_claim_evidences query."""

    @patch("apps.owasp.api.internal.queries.board_candidate_claim_evidence.BoardCandidateClaim")
    def test_board_candidate_claim_evidences_claim_not_found(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = MagicMock()
        user.github_user.login = "alice"
        info = _make_info(user)
        claim_key = "my-key"
        login = "alice"

        mock_claim_model.objects.filter.return_value.first.return_value = None

        query = BoardCandidateClaimEvidenceQuery()
        result = query.board_candidate_claim_evidences(
            info, claim_key=claim_key, login=login, year=2025
        )

        assert result == []

    @patch("apps.owasp.api.internal.queries.board_candidate_claim_evidence.BoardCandidateClaim")
    def test_board_candidate_claim_evidences_self(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        claim_key = "my-key"
        login = "alice"

        claim = MagicMock()
        claim.candidate.member = mock_github_user
        evidences_qs = MagicMock()
        claim.evidences.filter.return_value = evidences_qs
        mock_claim_model.objects.filter.return_value.first.return_value = claim

        query = BoardCandidateClaimEvidenceQuery()
        result = query.board_candidate_claim_evidences(
            info, claim_key=claim_key, login=login, year=2025
        )

        claim.evidences.filter.assert_called_once_with(is_removed=False)
        assert result == evidences_qs

    @patch("apps.owasp.api.internal.queries.board_candidate_claim_evidence.BoardCandidateClaim")
    def test_board_candidate_claim_evidences_non_self_non_approved(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = MagicMock()
        info = _make_info(user)
        claim_key = "my-key"
        login = "alice"

        claim = MagicMock()
        claim.candidate.member = MagicMock()
        claim.status = BoardCandidateClaim.Status.SUBMITTED
        mock_claim_model.objects.filter.return_value.first.return_value = claim

        query = BoardCandidateClaimEvidenceQuery()
        result = query.board_candidate_claim_evidences(
            info, claim_key=claim_key, login=login, year=2025
        )

        assert result == []

    @patch("apps.owasp.api.internal.queries.board_candidate_claim_evidence.BoardCandidateClaim")
    def test_board_candidate_claim_evidences_non_self_approved(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = MagicMock()
        info = _make_info(user)
        claim_key = "my-key"
        login = "alice"

        claim = MagicMock()
        claim.candidate.member = MagicMock()
        claim.status = mock_claim_model.Status.APPROVED
        evidences_qs = MagicMock()
        claim.evidences.filter.return_value = evidences_qs
        mock_claim_model.objects.filter.return_value.first.return_value = claim

        query = BoardCandidateClaimEvidenceQuery()
        result = query.board_candidate_claim_evidences(
            info, claim_key=claim_key, login=login, year=2025
        )

        claim.evidences.filter.assert_called_once_with(is_removed=False)
        assert result == evidences_qs
