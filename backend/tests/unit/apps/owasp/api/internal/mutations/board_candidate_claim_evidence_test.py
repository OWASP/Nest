"""Tests for BoardCandidateClaimEvidence mutations."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pydantic
import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from apps.owasp.api.internal.mutations.board_candidate_claim_evidence import (
    BoardCandidateClaimEvidenceMutations,
    CreateEvidencePydanticInput,
    RemoveEvidencePydanticInput,
    UpdateEvidencePydanticInput,
)
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from apps.owasp.models.board_candidate_claim_evidence import BoardCandidateClaimEvidence


@pytest.fixture(autouse=True)
def _mock_transaction_atomic():
    """Disable transaction.atomic decorator for all tests."""
    with (
        patch("django.db.transaction.Atomic.__enter__", return_value=None),
        patch("django.db.transaction.Atomic.__exit__", return_value=False),
        patch("django.db.transaction.on_commit", side_effect=lambda f, **_: f()),
    ):
        yield


def _make_info(user):
    info = MagicMock()
    info.context.request.user = user
    return info


class TestCreateBoardCandidateClaimEvidence:
    """Tests for create_board_candidate_claim_evidence mutation."""

    def _make_input_data(
        self,
        claim_key="test-key",
        name="Test Evidence",
        source_url="https://example.com",
        year=2025,
    ):
        input_data = MagicMock(
            claim_key=claim_key,
            description="Test description.",
            file=None,
            source_url=source_url,
        )
        input_data.name = name
        input_data.year = year
        input_data.to_pydantic.return_value = input_data
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
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data(claim_key="non-existent")

        mock_claim_model.DoesNotExist = BoardCandidateClaim.DoesNotExist
        mock_claim_model.objects.select_for_update.return_value.get.side_effect = (
            BoardCandidateClaim.DoesNotExist
        )

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.create_board_candidate_claim_evidence(info, input_data)

        assert not result.ok
        assert result.code == "NOT_FOUND"

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
        self,
        evidence_key="test-evidence-key",
        name="Updated Evidence",
        source_url="https://updated.com",
        claim_key="test-claim-key",
        year=2025,
    ):
        input_data = MagicMock(
            key=evidence_key,
            description="Updated description.",
            file=None,
            source_url=source_url,
        )
        input_data.name = name
        input_data.claim_key = claim_key
        input_data.year = year
        input_data.to_pydantic.return_value = input_data
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
            key="test-evidence-key",
            description=None,
            file=None,
            source_url=None,
        )
        input_data.name = "Updated Name"
        input_data.claim_key = "test-claim-key"
        input_data.year = 2025
        input_data.to_pydantic.return_value = input_data

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
        assert evidence.source_url == ""
        evidence.save.assert_called_once_with(update_fields=["name", "key", "source_url"])

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
            key="test-evidence-key",
            name=None,
            description=None,
            file=MagicMock(),
            source_url=None,
        )
        input_data.claim_key = "test-claim-key"
        input_data.year = 2025
        input_data.to_pydantic.return_value = input_data

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
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data(evidence_key="non-existent")

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

    def _make_input_data(
        self,
        evidence_key="test-evidence-key",
        removed_reason="No longer relevant",
        claim_key="test-claim-key",
        year=2025,
    ):
        data = MagicMock(
            key=evidence_key,
            removed_reason=removed_reason,
            claim_key=claim_key,
            year=year,
        )
        data.to_pydantic.return_value = data
        return data

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
            update_fields=["file", "is_removed", "removed_reason", "removed_at"]
        )

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.BoardCandidateClaim")
    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_evidence"
        ".BoardCandidateClaimEvidence"
    )
    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_evidence.timezone")
    def test_remove_without_reason(self, mock_timezone, mock_evidence_model, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        mock_evidence_model.REMOVAL_ALLOWED_STATUSES = (
            BoardCandidateClaimEvidence.REMOVAL_ALLOWED_STATUSES
        )
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data(removed_reason=None)
        now = datetime(2024, 1, 1, tzinfo=UTC)
        mock_timezone.now.return_value = now

        evidence = MagicMock()
        evidence.claim.candidate.member = mock_github_user
        evidence.claim.status = BoardCandidateClaim.Status.DRAFT
        mock_evidence_model.objects.select_for_update.return_value.get.return_value = evidence

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.remove_board_candidate_claim_evidence(info, input_data)

        assert result.ok
        assert result.code == "SUCCESS"
        assert evidence.removed_reason == ""

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
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data(evidence_key="non-existent")

        mock_evidence_model.DoesNotExist = BoardCandidateClaimEvidence.DoesNotExist
        mock_evidence_model.objects.select_for_update.return_value.get.side_effect = (
            BoardCandidateClaimEvidence.DoesNotExist
        )

        mutation = BoardCandidateClaimEvidenceMutations()
        result = mutation.remove_board_candidate_claim_evidence(info, input_data)

        assert not result.ok
        assert result.code == "NOT_FOUND"

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


class TestCreateEvidencePydanticValidation:
    """Tests for CreateEvidencePydanticInput and its resolver handling."""

    def test_pydantic_rejects_name_over_max_length(self):
        with pytest.raises(pydantic.ValidationError) as exc_info:
            CreateEvidencePydanticInput(claim_key="k", description="d", name="x" * 201, year=2025)

        assert any(err["loc"] == ("name",) for err in exc_info.value.errors())

    @pytest.mark.parametrize("bad_url", ["not a url", "javascript:alert(1)", "ftp:/host", "://x"])
    def test_pydantic_rejects_invalid_source_url(self, bad_url):
        with pytest.raises(pydantic.ValidationError) as exc_info:
            CreateEvidencePydanticInput(
                claim_key="k", description="d", name="n", source_url=bad_url, year=2025
            )

        assert any(err["loc"] == ("source_url",) for err in exc_info.value.errors())

    @pytest.mark.parametrize("url", [None, "https://example.com/path?q=1"])
    def test_pydantic_accepts_absent_or_valid_source_url(self, url):
        model = CreateEvidencePydanticInput(
            claim_key="k", description="d", name="n", source_url=url, year=2025
        )

        if url:
            assert model.source_url.host == "example.com"
            assert model.source_url.scheme == "https"
        else:
            assert model.source_url is None

    def test_resolver_returns_field_errors_when_pydantic_fails(self):
        with pytest.raises(pydantic.ValidationError) as exc_info:
            CreateEvidencePydanticInput(claim_key="x" * 101, description="d", name="n", year=2025)

        data = MagicMock()
        data.to_pydantic.side_effect = exc_info.value
        info = _make_info(MagicMock())

        result = BoardCandidateClaimEvidenceMutations().create_board_candidate_claim_evidence(
            info, data
        )

        assert not result.ok
        assert result.code == "VALIDATION_ERROR"
        assert result.field_errors is not None
        assert {fe.field for fe in result.field_errors} == {"claimKey"}


class TestUpdateEvidencePydanticValidation:
    """Tests for UpdateEvidencePydanticInput and its resolver handling."""

    def test_pydantic_rejects_key_over_max_length(self):
        with pytest.raises(pydantic.ValidationError) as exc_info:
            UpdateEvidencePydanticInput(claim_key="k", key="x" * 101, year=2025)

        assert any(err["loc"] == ("key",) for err in exc_info.value.errors())

    def test_pydantic_rejects_invalid_source_url(self):
        with pytest.raises(pydantic.ValidationError) as exc_info:
            UpdateEvidencePydanticInput(claim_key="k", key="e", source_url="not-a-url", year=2025)

        assert any(err["loc"] == ("source_url",) for err in exc_info.value.errors())

    def test_pydantic_accepts_valid_source_url(self):
        model = UpdateEvidencePydanticInput(
            claim_key="k", key="e", source_url="https://example.com/x", year=2025
        )

        assert model.source_url.host == "example.com"
        assert model.source_url.scheme == "https"

    def test_resolver_returns_field_errors_when_pydantic_fails(self):
        with pytest.raises(pydantic.ValidationError) as exc_info:
            UpdateEvidencePydanticInput(claim_key="k", key="x" * 101, year=2025)

        data = MagicMock()
        data.to_pydantic.side_effect = exc_info.value
        info = _make_info(MagicMock())

        result = BoardCandidateClaimEvidenceMutations().update_board_candidate_claim_evidence(
            info, data
        )

        assert not result.ok
        assert result.code == "VALIDATION_ERROR"
        assert result.field_errors is not None
        assert {fe.field for fe in result.field_errors} == {"key"}


class TestRemoveEvidencePydanticValidation:
    """Tests for RemoveEvidencePydanticInput and its resolver handling."""

    def test_pydantic_rejects_key_over_max_length(self):
        with pytest.raises(pydantic.ValidationError) as exc_info:
            RemoveEvidencePydanticInput(claim_key="k", key="x" * 101, year=2025)

        assert any(err["loc"] == ("key",) for err in exc_info.value.errors())

    def test_resolver_returns_field_errors_when_pydantic_fails(self):
        with pytest.raises(pydantic.ValidationError) as exc_info:
            RemoveEvidencePydanticInput(claim_key="k", key="x" * 101, year=2025)

        data = MagicMock()
        data.to_pydantic.side_effect = exc_info.value
        info = _make_info(MagicMock())

        result = BoardCandidateClaimEvidenceMutations().remove_board_candidate_claim_evidence(
            info, data
        )

        assert not result.ok
        assert result.code == "VALIDATION_ERROR"
        assert result.field_errors is not None
        assert {fe.field for fe in result.field_errors} == {"key"}
