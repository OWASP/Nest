"""Tests for BoardCandidateClaimEvidence GraphQL queries."""

from unittest.mock import MagicMock, patch

from apps.owasp.api.internal.queries.board_candidate_claim_evidence import (
    BoardCandidateClaimEvidenceQuery,
)
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from apps.owasp.models.board_candidate_claim_evidence import BoardCandidateClaimEvidence


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

        mock_claim_model.objects.filter.assert_called_once_with(
            candidate__member__login=login, key=claim_key, board__year=2025
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

        mock_claim_model.objects.filter.assert_called_once_with(
            candidate__member__login=login, key=claim_key, board__year=2025
        )
        claim.evidences.filter.assert_called_once_with(is_removed=False)
        assert result == evidences_qs

    @patch("apps.owasp.api.internal.queries.board_candidate_claim_evidence.BoardCandidateClaim")
    def test_board_candidate_claim_evidences_non_self_non_approved(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = MagicMock()
        user.github_user.is_owasp_staff = False
        user.github_user.is_claim_reviewer = False
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

        mock_claim_model.objects.filter.assert_called_once_with(
            candidate__member__login=login, key=claim_key, board__year=2025
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

        mock_claim_model.objects.filter.assert_called_once_with(
            candidate__member__login=login, key=claim_key, board__year=2025
        )
        claim.evidences.filter.assert_called_once_with(is_removed=False)
        assert result == evidences_qs

    @patch("apps.owasp.api.internal.queries.board_candidate_claim_evidence.BoardCandidateClaim")
    def test_board_candidate_claim_evidences_reviewer_sees_submitted(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = MagicMock()
        user.github_user.is_owasp_staff = True
        info = _make_info(user)
        claim_key = "my-key"
        login = "alice"

        claim = MagicMock()
        claim.candidate.member = MagicMock()
        claim.status = BoardCandidateClaim.Status.SUBMITTED
        evidences_qs = MagicMock()
        claim.evidences.filter.return_value = evidences_qs
        mock_claim_model.objects.filter.return_value.first.return_value = claim

        query = BoardCandidateClaimEvidenceQuery()
        result = query.board_candidate_claim_evidences(
            info, claim_key=claim_key, login=login, year=2025
        )

        mock_claim_model.objects.filter.assert_called_once_with(
            candidate__member__login=login, key=claim_key, board__year=2025
        )
        claim.evidences.filter.assert_called_once_with(is_removed=False)
        assert result == evidences_qs


class TestBoardCandidateClaimEvidenceSingleQuery:
    """Tests for board_candidate_claim_evidence single evidence query."""

    def test_board_candidate_claim_evidence_self(self):
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)

        evidence = MagicMock()
        evidence.claim.candidate.member = mock_github_user
        evidence.claim.status = BoardCandidateClaim.Status.DRAFT

        with patch(
            "apps.owasp.api.internal.queries.board_candidate_claim_evidence"
            ".BoardCandidateClaimEvidence"
        ) as mock_evidence_model:
            mock_evidence_model.DoesNotExist = BoardCandidateClaimEvidence.DoesNotExist
            mock_evidence_model.objects.get.return_value = evidence

            query = BoardCandidateClaimEvidenceQuery()
            result = query.board_candidate_claim_evidence(
                info, claim_key="test-key", key="ev-key", login="alice", year=2025
            )

        mock_evidence_model.objects.get.assert_called_once_with(
            claim__key="test-key",
            key="ev-key",
            claim__candidate__member__login="alice",
            claim__board__year=2025,
            is_removed=False,
        )
        assert result == evidence

    def test_board_candidate_claim_evidence_non_self_approved(self):
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = MagicMock()
        info = _make_info(user)

        evidence = MagicMock()
        evidence.claim.candidate.member = MagicMock()
        evidence.claim.status = BoardCandidateClaim.Status.APPROVED

        with patch(
            "apps.owasp.api.internal.queries.board_candidate_claim_evidence"
            ".BoardCandidateClaimEvidence"
        ) as mock_evidence_model:
            mock_evidence_model.DoesNotExist = BoardCandidateClaimEvidence.DoesNotExist
            mock_evidence_model.objects.get.return_value = evidence

            query = BoardCandidateClaimEvidenceQuery()
            result = query.board_candidate_claim_evidence(
                info, claim_key="test-key", key="ev-key", login="alice", year=2025
            )

        assert result == evidence

    def test_board_candidate_claim_evidence_non_self_not_approved(self):
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = MagicMock()
        user.github_user.is_owasp_staff = False
        user.github_user.is_claim_reviewer = False
        info = _make_info(user)

        evidence = MagicMock()
        evidence.claim.candidate.member = MagicMock()
        evidence.claim.status = BoardCandidateClaim.Status.SUBMITTED

        with patch(
            "apps.owasp.api.internal.queries.board_candidate_claim_evidence"
            ".BoardCandidateClaimEvidence"
        ) as mock_evidence_model:
            mock_evidence_model.DoesNotExist = BoardCandidateClaimEvidence.DoesNotExist
            mock_evidence_model.objects.get.return_value = evidence

            query = BoardCandidateClaimEvidenceQuery()
            result = query.board_candidate_claim_evidence(
                info, claim_key="test-key", key="ev-key", login="alice", year=2025
            )

        assert result is None

    def test_board_candidate_claim_evidence_not_found(self):
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = MagicMock()
        info = _make_info(user)

        with patch(
            "apps.owasp.api.internal.queries.board_candidate_claim_evidence"
            ".BoardCandidateClaimEvidence"
        ) as mock_evidence_model:
            mock_evidence_model.DoesNotExist = BoardCandidateClaimEvidence.DoesNotExist
            mock_evidence_model.objects.get.side_effect = BoardCandidateClaimEvidence.DoesNotExist

            query = BoardCandidateClaimEvidenceQuery()
            result = query.board_candidate_claim_evidence(
                info, claim_key="test-key", key="ev-key", login="alice", year=2025
            )

        assert result is None

    def test_board_candidate_claim_evidence_reviewer_sees_submitted(self):
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = MagicMock()
        user.github_user.is_claim_reviewer = True
        info = _make_info(user)

        evidence = MagicMock()
        evidence.claim.candidate.member = MagicMock()
        evidence.claim.status = BoardCandidateClaim.Status.SUBMITTED

        with patch(
            "apps.owasp.api.internal.queries.board_candidate_claim_evidence"
            ".BoardCandidateClaimEvidence"
        ) as mock_evidence_model:
            mock_evidence_model.DoesNotExist = BoardCandidateClaimEvidence.DoesNotExist
            mock_evidence_model.objects.get.return_value = evidence

            query = BoardCandidateClaimEvidenceQuery()
            result = query.board_candidate_claim_evidence(
                info, claim_key="test-key", key="ev-key", login="alice", year=2025
            )

        assert result == evidence


class TestBoardCandidateClaimEvidenceFileUrlQuery:
    """Tests for board_candidate_claim_evidence_file_url query."""

    def test_file_url_accessible_with_file(self):
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)

        evidence = MagicMock()
        evidence.claim.candidate.member = mock_github_user
        evidence.claim.status = BoardCandidateClaim.Status.DRAFT
        evidence.file = MagicMock()
        evidence.file.url = "/media/test.pdf"

        with patch(
            "apps.owasp.api.internal.queries.board_candidate_claim_evidence"
            ".BoardCandidateClaimEvidence"
        ) as mock_evidence_model:
            mock_evidence_model.DoesNotExist = BoardCandidateClaimEvidence.DoesNotExist
            mock_evidence_model.objects.get.return_value = evidence
            info.context.request.build_absolute_uri.return_value = (
                "https://example.com/media/test.pdf"
            )

            query = BoardCandidateClaimEvidenceQuery()
            result = query.board_candidate_claim_evidence_file_url(
                info, claim_key="test-key", key="ev-key", login="alice", year=2025
            )

        assert result == "https://example.com/media/test.pdf"

    def test_file_url_accessible_no_file(self):
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)

        evidence = MagicMock()
        evidence.claim.candidate.member = mock_github_user
        evidence.claim.status = BoardCandidateClaim.Status.DRAFT
        evidence.file = None

        with patch(
            "apps.owasp.api.internal.queries.board_candidate_claim_evidence"
            ".BoardCandidateClaimEvidence"
        ) as mock_evidence_model:
            mock_evidence_model.DoesNotExist = BoardCandidateClaimEvidence.DoesNotExist
            mock_evidence_model.objects.get.return_value = evidence

            query = BoardCandidateClaimEvidenceQuery()
            result = query.board_candidate_claim_evidence_file_url(
                info, claim_key="test-key", key="ev-key", login="alice", year=2025
            )

        assert result is None

    def test_file_url_not_accessible(self):
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = MagicMock()
        user.github_user.is_owasp_staff = False
        user.github_user.is_claim_reviewer = False
        info = _make_info(user)

        evidence = MagicMock()
        evidence.claim.candidate.member = MagicMock()
        evidence.claim.status = BoardCandidateClaim.Status.SUBMITTED
        evidence.file = MagicMock()
        evidence.file.url = "/media/test.pdf"

        with patch(
            "apps.owasp.api.internal.queries.board_candidate_claim_evidence"
            ".BoardCandidateClaimEvidence"
        ) as mock_evidence_model:
            mock_evidence_model.DoesNotExist = BoardCandidateClaimEvidence.DoesNotExist
            mock_evidence_model.objects.get.return_value = evidence

            query = BoardCandidateClaimEvidenceQuery()
            result = query.board_candidate_claim_evidence_file_url(
                info, claim_key="test-key", key="ev-key", login="alice", year=2025
            )

        assert result is None

    def test_file_url_not_found(self):
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = MagicMock()
        info = _make_info(user)

        with patch(
            "apps.owasp.api.internal.queries.board_candidate_claim_evidence"
            ".BoardCandidateClaimEvidence"
        ) as mock_evidence_model:
            mock_evidence_model.DoesNotExist = BoardCandidateClaimEvidence.DoesNotExist
            mock_evidence_model.objects.get.side_effect = BoardCandidateClaimEvidence.DoesNotExist

            query = BoardCandidateClaimEvidenceQuery()
            result = query.board_candidate_claim_evidence_file_url(
                info, claim_key="test-key", key="ev-key", login="alice", year=2025
            )

        assert result is None

    def test_file_url_anonymous_approved(self):
        user = MagicMock()
        user.is_authenticated = False
        info = _make_info(user)

        evidence = MagicMock()
        evidence.claim.status = BoardCandidateClaim.Status.APPROVED
        evidence.file = MagicMock()
        evidence.file.url = "/media/test.pdf"

        with patch(
            "apps.owasp.api.internal.queries.board_candidate_claim_evidence"
            ".BoardCandidateClaimEvidence"
        ) as mock_evidence_model:
            mock_evidence_model.DoesNotExist = BoardCandidateClaimEvidence.DoesNotExist
            mock_evidence_model.objects.get.return_value = evidence
            info.context.request.build_absolute_uri.return_value = (
                "https://example.com/media/test.pdf"
            )

            query = BoardCandidateClaimEvidenceQuery()
            result = query.board_candidate_claim_evidence_file_url(
                info, claim_key="test-key", key="ev-key", login="alice", year=2025
            )

        assert result == "https://example.com/media/test.pdf"

    def test_file_url_reviewer_accessible(self):
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = MagicMock()
        user.github_user.is_owasp_staff = True
        info = _make_info(user)

        evidence = MagicMock()
        evidence.claim.candidate.member = MagicMock()
        evidence.claim.status = BoardCandidateClaim.Status.SUBMITTED
        evidence.file = MagicMock()
        evidence.file.url = "/media/test.pdf"

        with patch(
            "apps.owasp.api.internal.queries.board_candidate_claim_evidence"
            ".BoardCandidateClaimEvidence"
        ) as mock_evidence_model:
            mock_evidence_model.DoesNotExist = BoardCandidateClaimEvidence.DoesNotExist
            mock_evidence_model.objects.get.return_value = evidence
            info.context.request.build_absolute_uri.return_value = (
                "https://example.com/media/test.pdf"
            )

            query = BoardCandidateClaimEvidenceQuery()
            result = query.board_candidate_claim_evidence_file_url(
                info, claim_key="test-key", key="ev-key", login="alice", year=2025
            )

        assert result == "https://example.com/media/test.pdf"
