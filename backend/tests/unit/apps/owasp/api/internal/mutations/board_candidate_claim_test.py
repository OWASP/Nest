"""Tests for BoardCandidateClaim mutations."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from apps.owasp.api.internal.mutations.board_candidate_claim import (
    BoardCandidateClaimMutations,
    _validate_reorder_claims,
)
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim


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


class TestDiscardBoardCandidateClaim:
    """Tests for discard_board_candidate_claim mutation."""

    def _make_input_data(self, claim_id):
        return MagicMock(claim_id=MagicMock(node_id=claim_id))

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_discard_claim_success(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.__str__.return_value = "alice"
        info = _make_info(user)
        input_data = self._make_input_data(1)

        claim = MagicMock()
        claim.candidate.member.login = "alice"
        claim.status = BoardCandidateClaim.Status.DRAFT
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimMutations()
        result = mutation.discard_board_candidate_claim(info, input_data)

        assert result.ok
        assert result.code == "SUCCESS"
        assert claim.status == BoardCandidateClaim.Status.DISCARDED
        claim.save.assert_called_once()

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_discard_claim_not_found(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.__str__.return_value = "alice"
        info = _make_info(user)
        input_data = self._make_input_data(99)

        mock_claim_model.DoesNotExist = BoardCandidateClaim.DoesNotExist
        mock_claim_model.objects.select_for_update.return_value.get.side_effect = (
            BoardCandidateClaim.DoesNotExist
        )

        mutation = BoardCandidateClaimMutations()
        result = mutation.discard_board_candidate_claim(info, input_data)

        assert not result.ok
        assert result.code == "NOT_FOUND"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_discard_claim_forbidden(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.__str__.return_value = "bob"
        info = _make_info(user)
        input_data = self._make_input_data(1)

        claim = MagicMock()
        claim.candidate.member.login = "alice"
        claim.status = BoardCandidateClaim.Status.DRAFT
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimMutations()
        result = mutation.discard_board_candidate_claim(info, input_data)

        assert not result.ok
        assert result.code == "FORBIDDEN"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_discard_claim_invalid_status(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.__str__.return_value = "alice"
        info = _make_info(user)
        input_data = self._make_input_data(1)

        claim = MagicMock()
        claim.candidate.member.login = "alice"
        claim.status = BoardCandidateClaim.Status.SUBMITTED
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimMutations()
        result = mutation.discard_board_candidate_claim(info, input_data)

        assert not result.ok
        assert result.code == "INVALID_STATUS"


class TestSubmitBoardCandidateClaim:
    """Tests for submit_board_candidate_claim mutation."""

    def _make_input_data(self, claim_id):
        return MagicMock(claim_id=MagicMock(node_id=claim_id))

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_submit_claim_success(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.__str__.return_value = "alice"
        info = _make_info(user)
        input_data = self._make_input_data(1)

        claim = MagicMock()
        claim.candidate.member.login = "alice"
        claim.status = BoardCandidateClaim.Status.DRAFT
        claim.evidences.filter.return_value.exists.return_value = True
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimMutations()
        result = mutation.submit_board_candidate_claim(info, input_data)

        assert result.ok
        assert result.code == "SUCCESS"
        assert claim.status == BoardCandidateClaim.Status.SUBMITTED
        claim.save.assert_called_once()

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_submit_claim_missing_evidence(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.__str__.return_value = "alice"
        info = _make_info(user)
        input_data = self._make_input_data(1)

        claim = MagicMock()
        claim.candidate.member.login = "alice"
        claim.status = BoardCandidateClaim.Status.DRAFT
        claim.evidences.filter.return_value.exists.return_value = False
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimMutations()
        result = mutation.submit_board_candidate_claim(info, input_data)

        assert not result.ok
        assert result.code == "VALIDATION_ERROR"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_submit_claim_invalid_status(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.__str__.return_value = "alice"
        info = _make_info(user)
        input_data = self._make_input_data(1)

        claim = MagicMock()
        claim.candidate.member.login = "alice"
        claim.status = BoardCandidateClaim.Status.SUBMITTED
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimMutations()
        result = mutation.submit_board_candidate_claim(info, input_data)

        assert not result.ok
        assert result.code == "INVALID_STATUS"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_submit_claim_forbidden(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.__str__.return_value = "bob"
        info = _make_info(user)
        input_data = self._make_input_data(1)

        claim = MagicMock()
        claim.candidate.member.login = "alice"
        claim.status = BoardCandidateClaim.Status.DRAFT
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimMutations()
        result = mutation.submit_board_candidate_claim(info, input_data)

        assert not result.ok
        assert result.code == "FORBIDDEN"


class TestWithdrawBoardCandidateClaim:
    """Tests for withdraw_board_candidate_claim mutation."""

    def _make_input_data(self, claim_id, withdrawn_reason="No longer relevant"):
        return MagicMock(
            claim_id=MagicMock(node_id=claim_id),
            withdrawn_reason=withdrawn_reason,
        )

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.timezone")
    def test_withdraw_claim_success_submitted(self, mock_timezone, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.__str__.return_value = "alice"
        info = _make_info(user)
        input_data = self._make_input_data(1)
        now = datetime(2024, 1, 1, tzinfo=UTC)
        mock_timezone.now.return_value = now

        claim = MagicMock()
        claim.candidate.member.login = "alice"
        claim.status = BoardCandidateClaim.Status.SUBMITTED
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimMutations()
        result = mutation.withdraw_board_candidate_claim(info, input_data)

        assert result.ok
        assert result.code == "SUCCESS"
        assert claim.status == BoardCandidateClaim.Status.WITHDRAWN
        assert claim.withdrawn_reason == "No longer relevant"
        assert claim.withdrawn_at == now
        claim.save.assert_called_once()

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.timezone")
    def test_withdraw_claim_success_approved(self, mock_timezone, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.__str__.return_value = "alice"
        info = _make_info(user)
        input_data = self._make_input_data(1)
        now = datetime(2024, 1, 1, tzinfo=UTC)
        mock_timezone.now.return_value = now

        claim = MagicMock()
        claim.candidate.member.login = "alice"
        claim.status = BoardCandidateClaim.Status.APPROVED
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimMutations()
        result = mutation.withdraw_board_candidate_claim(info, input_data)

        assert result.ok
        assert result.code == "SUCCESS"
        assert claim.status == BoardCandidateClaim.Status.WITHDRAWN
        assert claim.withdrawn_reason == "No longer relevant"
        assert claim.withdrawn_at == now

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_withdraw_claim_invalid_status(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.__str__.return_value = "alice"
        info = _make_info(user)
        input_data = self._make_input_data(1)

        claim = MagicMock()
        claim.candidate.member.login = "alice"
        claim.status = BoardCandidateClaim.Status.DRAFT
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimMutations()
        result = mutation.withdraw_board_candidate_claim(info, input_data)

        assert not result.ok
        assert result.code == "INVALID_STATUS"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_withdraw_claim_forbidden(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.__str__.return_value = "bob"
        info = _make_info(user)
        input_data = self._make_input_data(1)

        claim = MagicMock()
        claim.candidate.member.login = "alice"
        claim.status = BoardCandidateClaim.Status.SUBMITTED
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimMutations()
        result = mutation.withdraw_board_candidate_claim(info, input_data)

        assert not result.ok
        assert result.code == "FORBIDDEN"


class TestValidateReorderClaims:
    """Tests for _validate_reorder_claims helper."""

    def _make_input_data(self, claim_ids):
        return MagicMock(claim_ids=[MagicMock(node_id=cid) for cid in claim_ids])

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_validate_success(self, mock_claim_model):
        input_data = self._make_input_data([1, 2, 3])
        mock_claim_model.objects.filter.return_value.count.return_value = 3

        claim_ids, error = _validate_reorder_claims(input_data)

        assert claim_ids == [1, 2, 3]
        assert error is None

    def test_validate_invalid_id(self):
        input_data = MagicMock(claim_ids=[MagicMock(node_id="not_an_int")])

        claim_ids, error = _validate_reorder_claims(input_data)

        assert claim_ids == []
        assert error is not None
        assert not error.ok
        assert error.code == "NOT_FOUND"

    def test_validate_empty_input(self):
        input_data = self._make_input_data([])

        claim_ids, error = _validate_reorder_claims(input_data)

        assert claim_ids == []
        assert error is not None
        assert not error.ok
        assert error.code == "VALIDATION_ERROR"

    def test_validate_duplicate_ids(self):
        input_data = self._make_input_data([1, 1, 2])

        claim_ids, error = _validate_reorder_claims(input_data)

        assert claim_ids == [1, 1, 2]
        assert error is not None
        assert not error.ok
        assert error.code == "VALIDATION_ERROR"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_validate_missing_ids(self, mock_claim_model):
        input_data = self._make_input_data([1, 2])
        mock_claim_model.objects.filter.return_value.count.return_value = 1

        claim_ids, error = _validate_reorder_claims(input_data)

        assert claim_ids == [1, 2]
        assert error is not None
        assert not error.ok
        assert error.code == "NOT_FOUND"


class TestReorderBoardCandidateClaims:
    """Tests for reorder_board_candidate_claims mutation."""

    def _make_input_data(self, claim_ids):
        return MagicMock(claim_ids=[MagicMock(node_id=cid) for cid in claim_ids])

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_reorder_claims_success(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.__str__.return_value = "alice"
        info = _make_info(user)
        input_data = self._make_input_data([2, 1, 3])

        claim_a = MagicMock(id=1, status=BoardCandidateClaim.Status.DRAFT)
        claim_a.candidate.member.login = "alice"
        claim_a.candidate_id = 10
        claim_a.board_id = 20
        claim_b = MagicMock(id=2, status=BoardCandidateClaim.Status.DRAFT)
        claim_b.candidate.member.login = "alice"
        claim_b.candidate_id = 10
        claim_b.board_id = 20
        claim_c = MagicMock(id=3, status=BoardCandidateClaim.Status.DRAFT)
        claim_c.candidate.member.login = "alice"
        claim_c.candidate_id = 10
        claim_c.board_id = 20

        mock_claim_model.objects.filter.return_value.count.return_value = 3
        mock_queryset = MagicMock()
        mock_queryset.select_related.return_value = [claim_a, claim_b, claim_c]
        mock_claim_model.objects.filter.return_value.select_for_update.return_value = mock_queryset

        filter_qs = mock_claim_model.objects.filter.return_value
        filter_qs.select_related.return_value.order_by.return_value = [
            claim_b,
            claim_a,
            claim_c,
        ]

        mutation = BoardCandidateClaimMutations()
        result = mutation.reorder_board_candidate_claims(info, input_data)

        assert result.ok
        assert result.code == "SUCCESS"
        assert result.claims == [claim_b, claim_a, claim_c]
        assert claim_b.order == 0
        assert claim_a.order == 1
        assert claim_c.order == 2
        mock_claim_model.objects.bulk_update.assert_called_once_with(
            [claim_a, claim_b, claim_c], ["order"]
        )

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_reorder_claims_empty_input(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.__str__.return_value = "alice"
        info = _make_info(user)
        input_data = self._make_input_data([])

        mutation = BoardCandidateClaimMutations()
        result = mutation.reorder_board_candidate_claims(info, input_data)

        assert not result.ok
        assert result.code == "VALIDATION_ERROR"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_reorder_claims_duplicate_ids(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.__str__.return_value = "alice"
        info = _make_info(user)
        input_data = self._make_input_data([1, 1, 2])

        mutation = BoardCandidateClaimMutations()
        result = mutation.reorder_board_candidate_claims(info, input_data)

        assert not result.ok
        assert result.code == "VALIDATION_ERROR"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_reorder_claims_missing_ids(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.__str__.return_value = "alice"
        info = _make_info(user)
        input_data = self._make_input_data([1, 2])

        mock_claim_model.objects.filter.return_value.count.return_value = 1

        mutation = BoardCandidateClaimMutations()
        result = mutation.reorder_board_candidate_claims(info, input_data)

        assert not result.ok
        assert result.code == "NOT_FOUND"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_reorder_claims_forbidden(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.__str__.return_value = "bob"
        info = _make_info(user)
        input_data = self._make_input_data([1, 2])

        claim_a = MagicMock(id=1, is_locked=False)
        claim_a.candidate.member.login = "alice"
        claim_a.candidate_id = 10
        claim_a.board_id = 20
        claim_b = MagicMock(id=2, is_locked=False)
        claim_b.candidate.member.login = "alice"
        claim_b.candidate_id = 10
        claim_b.board_id = 20

        mock_claim_model.objects.filter.return_value.count.return_value = 2
        mock_queryset = MagicMock()
        mock_queryset.select_related.return_value = [claim_a, claim_b]
        mock_claim_model.objects.filter.return_value.select_for_update.return_value = mock_queryset

        mutation = BoardCandidateClaimMutations()
        result = mutation.reorder_board_candidate_claims(info, input_data)

        assert not result.ok
        assert result.code == "FORBIDDEN"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_reorder_claims_mixed_candidates(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.__str__.return_value = "alice"
        info = _make_info(user)
        input_data = self._make_input_data([1, 2])

        claim_a = MagicMock(id=1, is_locked=False)
        claim_a.candidate.member.login = "alice"
        claim_a.candidate_id = 10
        claim_a.board_id = 20
        claim_b = MagicMock(id=2, is_locked=False)
        claim_b.candidate.member.login = "alice"
        claim_b.candidate_id = 11
        claim_b.board_id = 20

        mock_claim_model.objects.filter.return_value.count.return_value = 2
        mock_queryset = MagicMock()
        mock_queryset.select_related.return_value = [claim_a, claim_b]
        mock_claim_model.objects.filter.return_value.select_for_update.return_value = mock_queryset

        mutation = BoardCandidateClaimMutations()
        result = mutation.reorder_board_candidate_claims(info, input_data)

        assert not result.ok
        assert result.code == "VALIDATION_ERROR"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_reorder_claims_invalid_status(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.__str__.return_value = "alice"
        info = _make_info(user)
        input_data = self._make_input_data([1, 2])

        claim_a = MagicMock(id=1, status=BoardCandidateClaim.Status.SUBMITTED)
        claim_a.candidate.member.login = "alice"
        claim_a.candidate_id = 10
        claim_a.board_id = 20
        claim_b = MagicMock(id=2, status=BoardCandidateClaim.Status.SUBMITTED)
        claim_b.candidate.member.login = "alice"
        claim_b.candidate_id = 10
        claim_b.board_id = 20

        mock_claim_model.objects.filter.return_value.count.return_value = 2
        mock_queryset = MagicMock()
        mock_queryset.select_related.return_value = [claim_a, claim_b]
        mock_claim_model.objects.filter.return_value.select_for_update.return_value = mock_queryset

        mutation = BoardCandidateClaimMutations()
        result = mutation.reorder_board_candidate_claims(info, input_data)

        assert not result.ok
        assert result.code == "VALIDATION_ERROR"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_reorder_claims_mixed_boards(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.__str__.return_value = "alice"
        info = _make_info(user)
        input_data = self._make_input_data([1, 2])

        claim_a = MagicMock(id=1, is_locked=False)
        claim_a.candidate.member.login = "alice"
        claim_a.candidate_id = 10
        claim_a.board_id = 20
        claim_b = MagicMock(id=2, is_locked=False)
        claim_b.candidate.member.login = "alice"
        claim_b.candidate_id = 10
        claim_b.board_id = 21

        mock_claim_model.objects.filter.return_value.count.return_value = 2
        mock_queryset = MagicMock()
        mock_queryset.select_related.return_value = [claim_a, claim_b]
        mock_claim_model.objects.filter.return_value.select_for_update.return_value = mock_queryset

        mutation = BoardCandidateClaimMutations()
        result = mutation.reorder_board_candidate_claims(info, input_data)

        assert not result.ok
        assert result.code == "VALIDATION_ERROR"
