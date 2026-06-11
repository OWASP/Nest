"""Tests for BoardCandidateClaimEvidence mutations."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from apps.owasp.api.internal.mutations.board_candidate_claim_evidence import (
    BoardCandidateClaimEvidenceMutations,
)
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from apps.owasp.models.board_candidate_claim_evidence import BoardCandidateClaimEvidence


@pytest.fixture(autouse=True)
def _mock_transaction_atomic():
    """Disable transaction.atomic decorator for all tests."""
    with (
        patch("django.db.transaction.Atomic.__enter__", return_value=None),
        patch("django.db.transaction.Atomic.__exit__", return_value=False),
    ):
        yield


def _make_info(user):
    info = MagicMock()
    info.context.request.user = user
    return info


class TestCreateBoardCandidateClaimEvidence:
    """Tests for create_board_candidate_claim_evidence mutation."""

    def _make_input_data(self, claim_id=1, name="Test Evidence", source_url="https://example.com"):
        input_data = MagicMock(
            claim_id=MagicMock(node_id=str(claim_id)),
            description="Test description.",
            file=None,
            source_url=source_url,
        )
        input_data.name = name
        return input_data

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.BoardCandidateClaim")
    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_evidence"
        ".BoardCandidateClaimEvidence"
    )
    def test_create_success(self, mock_evidence_model, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data()

        claim = MagicMock()
        claim.candidate.member = mock_github_user
        claim.id = 1
        claim.status = BoardCandidateClaim.Status.DRAFT
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        evidence = MagicMock()
        mock_evidence_model.objects.create.return_value = evidence

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.create_board_candidate_claim_evidence(info, input_data)

        assert result.ok
        assert result.code == "SUCCESS"
        assert result.evidence == evidence
        mock_evidence_model.objects.create.assert_called_once_with(
            claim=claim,
            name=input_data.name,
            description=input_data.description,
            file=None,
            source_url=input_data.source_url,
        )

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.BoardCandidateClaim")
    def test_create_claim_not_found(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        info = _make_info(user)
        input_data = self._make_input_data(claim_id=99)

        mock_claim_model.DoesNotExist = BoardCandidateClaim.DoesNotExist
        mock_claim_model.objects.select_for_update.return_value.get.side_effect = (
            BoardCandidateClaim.DoesNotExist
        )

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.create_board_candidate_claim_evidence(info, input_data)

        assert not result.ok
        assert result.code == "NOT_FOUND"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.BoardCandidateClaim")
    def test_create_invalid_claim_id_returns_not_found(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        mock_claim_model.DoesNotExist = BoardCandidateClaim.DoesNotExist
        user = MagicMock()
        user.is_authenticated = True
        info = _make_info(user)
        input_data = self._make_input_data(claim_id="not_an_int")

        mock_claim_model.objects.select_for_update.return_value.get.side_effect = ValueError

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.create_board_candidate_claim_evidence(info, input_data)

        assert not result.ok
        assert result.code == "NOT_FOUND"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.BoardCandidateClaim")
    def test_create_forbidden(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = MagicMock()
        info = _make_info(user)
        input_data = self._make_input_data()

        claim = MagicMock()
        claim.candidate.member = MagicMock()
        claim.status = BoardCandidateClaim.Status.DRAFT
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.create_board_candidate_claim_evidence(info, input_data)

        assert not result.ok
        assert result.code == "FORBIDDEN"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.BoardCandidateClaim")
    def test_create_invalid_status(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data()

        claim = MagicMock()
        claim.candidate.member = mock_github_user
        claim.status = BoardCandidateClaim.Status.SUBMITTED
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.create_board_candidate_claim_evidence(info, input_data)

        assert not result.ok
        assert result.code == "INVALID_STATUS"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.BoardCandidateClaim")
    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_evidence"
        ".BoardCandidateClaimEvidence"
    )
    def test_create_integrity_error(self, mock_evidence_model, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data()

        claim = MagicMock()
        claim.candidate.member = mock_github_user
        claim.id = 1
        claim.status = BoardCandidateClaim.Status.DRAFT
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mock_evidence_model.objects.create.side_effect = IntegrityError

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.create_board_candidate_claim_evidence(info, input_data)

        assert not result.ok
        assert result.code == "ERROR"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.BoardCandidateClaim")
    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_evidence"
        ".BoardCandidateClaimEvidence"
    )
    def test_create_validation_error(self, mock_evidence_model, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data()

        claim = MagicMock()
        claim.candidate.member = mock_github_user
        claim.id = 1
        claim.status = BoardCandidateClaim.Status.DRAFT
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mock_evidence_model.objects.create.side_effect = ValidationError(
            {"source_url": ["This field is required."]}
        )

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.create_board_candidate_claim_evidence(info, input_data)

        assert not result.ok
        assert result.code == "VALIDATION_ERROR"


class TestUpdateBoardCandidateClaimEvidence:
    """Tests for update_board_candidate_claim_evidence mutation."""

    def _make_input_data(
        self, evidence_id=1, name="Updated Evidence", source_url="https://updated.com"
    ):
        input_data = MagicMock(
            evidence_id=MagicMock(node_id=str(evidence_id)),
            description="Updated description.",
            file=None,
            source_url=source_url,
        )
        input_data.name = name
        return input_data

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.BoardCandidateClaim")
    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_evidence"
        ".BoardCandidateClaimEvidence"
    )
    def test_update_success(self, mock_evidence_model, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data()

        evidence = MagicMock()
        evidence.claim.candidate.member = mock_github_user
        evidence.claim.status = BoardCandidateClaim.Status.DRAFT
        evidence.file = None
        mock_evidence_model.objects.select_for_update.return_value.get.return_value = evidence

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.update_board_candidate_claim_evidence(info, input_data)

        assert result.ok
        assert result.code == "SUCCESS"
        assert evidence.name == input_data.name
        assert evidence.description == input_data.description
        assert evidence.source_url == input_data.source_url
        evidence.save.assert_called_once()

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.BoardCandidateClaim")
    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_evidence"
        ".BoardCandidateClaimEvidence"
    )
    def test_update_partial_success(self, mock_evidence_model, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = MagicMock(
            evidence_id=MagicMock(node_id="1"),
            description=None,
            file=None,
            source_url=None,
        )
        input_data.name = "Updated Name"

        evidence = MagicMock()
        evidence.claim.candidate.member = mock_github_user
        evidence.claim.status = BoardCandidateClaim.Status.DRAFT
        evidence.file = None
        mock_evidence_model.objects.select_for_update.return_value.get.return_value = evidence

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.update_board_candidate_claim_evidence(info, input_data)

        assert result.ok
        assert result.code == "SUCCESS"
        assert evidence.name == "Updated Name"
        evidence.save.assert_called_once_with(update_fields=["name"])

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.BoardCandidateClaim")
    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_evidence"
        ".BoardCandidateClaimEvidence"
    )
    def test_update_with_file_replacement(self, mock_evidence_model, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        old_file = MagicMock()
        old_file.name = "old.pdf"
        input_data = MagicMock(
            evidence_id=MagicMock(node_id="1"),
            name=None,
            description=None,
            file=MagicMock(),
            source_url=None,
        )

        evidence = MagicMock()
        evidence.claim.candidate.member = mock_github_user
        evidence.claim.status = BoardCandidateClaim.Status.DRAFT
        evidence.file = old_file
        mock_evidence_model.objects.select_for_update.return_value.get.return_value = evidence

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.update_board_candidate_claim_evidence(info, input_data)

        assert result.ok
        assert result.code == "SUCCESS"
        assert evidence.file == input_data.file
        evidence.save.assert_called_once()
        call_kwargs = evidence.save.call_args[1]
        assert "file" in call_kwargs.get("update_fields", [])
        assert "file_name" in call_kwargs.get("update_fields", [])
        assert "file_size" in call_kwargs.get("update_fields", [])

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.BoardCandidateClaim")
    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_evidence"
        ".BoardCandidateClaimEvidence"
    )
    def test_update_evidence_not_found(self, mock_evidence_model, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        info = _make_info(user)
        input_data = self._make_input_data(evidence_id=99)

        mock_evidence_model.DoesNotExist = BoardCandidateClaimEvidence.DoesNotExist
        mock_evidence_model.objects.select_for_update.return_value.get.side_effect = (
            BoardCandidateClaimEvidence.DoesNotExist
        )

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.update_board_candidate_claim_evidence(info, input_data)

        assert not result.ok
        assert result.code == "NOT_FOUND"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.BoardCandidateClaim")
    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_evidence"
        ".BoardCandidateClaimEvidence"
    )
    def test_update_invalid_evidence_id_returns_not_found(
        self, mock_evidence_model, mock_claim_model
    ):
        mock_claim_model.Status = BoardCandidateClaim.Status
        mock_evidence_model.DoesNotExist = BoardCandidateClaimEvidence.DoesNotExist
        user = MagicMock()
        user.is_authenticated = True
        info = _make_info(user)
        input_data = self._make_input_data(evidence_id="not_an_int")

        mock_evidence_model.objects.select_for_update.return_value.get.side_effect = ValueError

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.update_board_candidate_claim_evidence(info, input_data)

        assert not result.ok
        assert result.code == "NOT_FOUND"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.BoardCandidateClaim")
    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_evidence"
        ".BoardCandidateClaimEvidence"
    )
    def test_update_forbidden(self, mock_evidence_model, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = MagicMock()
        info = _make_info(user)
        input_data = self._make_input_data()

        evidence = MagicMock()
        evidence.claim.candidate.member = MagicMock()
        evidence.claim.status = BoardCandidateClaim.Status.DRAFT
        mock_evidence_model.objects.select_for_update.return_value.get.return_value = evidence

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.update_board_candidate_claim_evidence(info, input_data)

        assert not result.ok
        assert result.code == "FORBIDDEN"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.BoardCandidateClaim")
    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_evidence"
        ".BoardCandidateClaimEvidence"
    )
    def test_update_invalid_status(self, mock_evidence_model, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data()

        evidence = MagicMock()
        evidence.claim.candidate.member = mock_github_user
        evidence.claim.status = BoardCandidateClaim.Status.SUBMITTED
        mock_evidence_model.objects.select_for_update.return_value.get.return_value = evidence

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.update_board_candidate_claim_evidence(info, input_data)

        assert not result.ok
        assert result.code == "INVALID_STATUS"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.BoardCandidateClaim")
    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_evidence"
        ".BoardCandidateClaimEvidence"
    )
    def test_update_integrity_error(self, mock_evidence_model, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data()

        evidence = MagicMock()
        evidence.claim.candidate.member = mock_github_user
        evidence.claim.status = BoardCandidateClaim.Status.DRAFT
        evidence.file = None
        evidence.save.side_effect = IntegrityError
        mock_evidence_model.objects.select_for_update.return_value.get.return_value = evidence

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.update_board_candidate_claim_evidence(info, input_data)

        assert not result.ok
        assert result.code == "ERROR"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.BoardCandidateClaim")
    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_evidence"
        ".BoardCandidateClaimEvidence"
    )
    def test_update_validation_error(self, mock_evidence_model, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data()

        evidence = MagicMock()
        evidence.claim.candidate.member = mock_github_user
        evidence.claim.status = BoardCandidateClaim.Status.DRAFT
        evidence.file = None
        evidence.save.side_effect = ValidationError({"name": ["Invalid."]})
        mock_evidence_model.objects.select_for_update.return_value.get.return_value = evidence

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.update_board_candidate_claim_evidence(info, input_data)

        assert not result.ok
        assert result.code == "VALIDATION_ERROR"


class TestRemoveBoardCandidateClaimEvidence:
    """Tests for remove_board_candidate_claim_evidence mutation."""

    def _make_input_data(self, evidence_id=1, removed_reason="No longer relevant"):
        return MagicMock(
            evidence_id=MagicMock(node_id=str(evidence_id)),
            removed_reason=removed_reason,
        )

    @pytest.mark.parametrize(
        "status",
        [
            BoardCandidateClaim.Status.DRAFT,
            BoardCandidateClaim.Status.DISCARDED,
            BoardCandidateClaim.Status.WITHDRAWN,
        ],
    )
    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.BoardCandidateClaim")
    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_evidence"
        ".BoardCandidateClaimEvidence"
    )
    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.timezone")
    def test_remove_success(self, mock_timezone, mock_evidence_model, mock_claim_model, status):
        mock_claim_model.Status = BoardCandidateClaim.Status
        mock_evidence_model.REMOVAL_ALLOWED_STATUSES = (
            BoardCandidateClaimEvidence.REMOVAL_ALLOWED_STATUSES
        )
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data()
        now = datetime(2024, 1, 1, tzinfo=UTC)
        mock_timezone.now.return_value = now

        evidence = MagicMock()
        evidence.claim.candidate.member = mock_github_user
        evidence.claim.status = status
        mock_evidence_model.objects.select_for_update.return_value.get.return_value = evidence

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.remove_board_candidate_claim_evidence(info, input_data)

        assert result.ok
        assert result.code == "SUCCESS"
        assert evidence.is_removed is True
        assert evidence.removed_reason == "No longer relevant"
        assert evidence.removed_at == now
        evidence.save.assert_called_once_with(
            update_fields=["is_removed", "removed_reason", "removed_at"]
        )

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.BoardCandidateClaim")
    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_evidence"
        ".BoardCandidateClaimEvidence"
    )
    def test_remove_evidence_not_found(self, mock_evidence_model, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        mock_evidence_model.REMOVAL_ALLOWED_STATUSES = (
            BoardCandidateClaimEvidence.REMOVAL_ALLOWED_STATUSES
        )
        user = MagicMock()
        user.is_authenticated = True
        info = _make_info(user)
        input_data = self._make_input_data(evidence_id=99)

        mock_evidence_model.DoesNotExist = BoardCandidateClaimEvidence.DoesNotExist
        mock_evidence_model.objects.select_for_update.return_value.get.side_effect = (
            BoardCandidateClaimEvidence.DoesNotExist
        )

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.remove_board_candidate_claim_evidence(info, input_data)

        assert not result.ok
        assert result.code == "NOT_FOUND"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.BoardCandidateClaim")
    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_evidence"
        ".BoardCandidateClaimEvidence"
    )
    def test_remove_forbidden(self, mock_evidence_model, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        mock_evidence_model.REMOVAL_ALLOWED_STATUSES = (
            BoardCandidateClaimEvidence.REMOVAL_ALLOWED_STATUSES
        )
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = MagicMock()
        info = _make_info(user)
        input_data = self._make_input_data()

        evidence = MagicMock()
        evidence.claim.candidate.member = MagicMock()
        evidence.claim.status = BoardCandidateClaim.Status.DRAFT
        mock_evidence_model.objects.select_for_update.return_value.get.return_value = evidence

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.remove_board_candidate_claim_evidence(info, input_data)

        assert not result.ok
        assert result.code == "FORBIDDEN"

    @pytest.mark.parametrize(
        "status",
        [
            BoardCandidateClaim.Status.APPROVED,
            BoardCandidateClaim.Status.REJECTED,
            BoardCandidateClaim.Status.SUBMITTED,
        ],
    )
    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.BoardCandidateClaim")
    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_evidence"
        ".BoardCandidateClaimEvidence"
    )
    def test_remove_invalid_status(self, mock_evidence_model, mock_claim_model, status):
        mock_claim_model.Status = BoardCandidateClaim.Status
        mock_evidence_model.REMOVAL_ALLOWED_STATUSES = (
            BoardCandidateClaimEvidence.REMOVAL_ALLOWED_STATUSES
        )
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data()

        evidence = MagicMock()
        evidence.claim.candidate.member = mock_github_user
        evidence.claim.status = status
        mock_evidence_model.objects.select_for_update.return_value.get.return_value = evidence

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.remove_board_candidate_claim_evidence(info, input_data)

        assert not result.ok
        assert result.code == "INVALID_STATUS"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.BoardCandidateClaim")
    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_evidence"
        ".BoardCandidateClaimEvidence"
    )
    def test_remove_integrity_error(self, mock_evidence_model, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        mock_evidence_model.REMOVAL_ALLOWED_STATUSES = (
            BoardCandidateClaimEvidence.REMOVAL_ALLOWED_STATUSES
        )
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data()

        evidence = MagicMock()
        evidence.claim.candidate.member = mock_github_user
        evidence.claim.status = BoardCandidateClaim.Status.DRAFT
        evidence.save.side_effect = IntegrityError
        mock_evidence_model.objects.select_for_update.return_value.get.return_value = evidence

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.remove_board_candidate_claim_evidence(info, input_data)

        assert not result.ok
        assert result.code == "ERROR"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.BoardCandidateClaim")
    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_evidence"
        ".BoardCandidateClaimEvidence"
    )
    def test_remove_validation_error(self, mock_evidence_model, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        mock_evidence_model.REMOVAL_ALLOWED_STATUSES = (
            BoardCandidateClaimEvidence.REMOVAL_ALLOWED_STATUSES
        )
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data()

        evidence = MagicMock()
        evidence.claim.candidate.member = mock_github_user
        evidence.claim.status = BoardCandidateClaim.Status.DRAFT
        evidence.save.side_effect = ValidationError({"removed_reason": ["Required."]})
        mock_evidence_model.objects.select_for_update.return_value.get.return_value = evidence

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.remove_board_candidate_claim_evidence(info, input_data)

        assert not result.ok
        assert result.code == "VALIDATION_ERROR"
