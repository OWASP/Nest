"""Tests for BoardCandidateClaim mutations."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from apps.owasp.api.internal.mutations.board_candidate_claim import (
    BoardCandidateClaimMutations,
    _validate_reorder_claims,
)
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from apps.owasp.models.board_of_directors import BoardOfDirectors


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

    def _make_input_data(self, key, year=2025):
        return MagicMock(key=key, year=year)

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_discard_claim_success(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data("test-key")

        claim = MagicMock()
        claim.candidate.member = mock_github_user
        claim.status = BoardCandidateClaim.Status.DRAFT
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimMutations()
        result = mutation.discard_board_candidate_claim(info, input_data)

        assert result.ok
        assert result.code == "SUCCESS"
        assert result.claim is claim
        assert claim.status == BoardCandidateClaim.Status.DISCARDED
        claim.save.assert_called_once()

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_discard_claim_not_found(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data("non-existent")

        mock_claim_model.DoesNotExist = BoardCandidateClaim.DoesNotExist
        mock_claim_model.objects.select_for_update.return_value.get.side_effect = (
            BoardCandidateClaim.DoesNotExist
        )

        mutation = BoardCandidateClaimMutations()
        result = mutation.discard_board_candidate_claim(info, input_data)

        assert not result.ok
        assert result.code == "NOT_FOUND"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_discard_claim_invalid_status(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data("test-key")

        claim = MagicMock()
        claim.candidate.member = mock_github_user
        claim.status = BoardCandidateClaim.Status.SUBMITTED
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimMutations()
        result = mutation.discard_board_candidate_claim(info, input_data)

        assert not result.ok
        assert result.code == "INVALID_STATUS"


class TestSubmitBoardCandidateClaim:
    """Tests for submit_board_candidate_claim mutation."""

    def _make_input_data(self, key, year=2025):
        return MagicMock(key=key, year=year)

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_submit_claim_success(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data("test-key")

        claim = MagicMock()
        claim.candidate.member = mock_github_user
        claim.status = BoardCandidateClaim.Status.DRAFT
        claim.evidences.filter.return_value.exists.return_value = True
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimMutations()
        result = mutation.submit_board_candidate_claim(info, input_data)

        assert result.ok
        assert result.code == "SUCCESS"
        assert result.claim is claim
        assert claim.status == BoardCandidateClaim.Status.SUBMITTED
        claim.save.assert_called_once()

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_submit_claim_missing_evidence(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data("test-key")

        claim = MagicMock()
        claim.candidate.member = mock_github_user
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
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data("test-key")

        claim = MagicMock()
        claim.candidate.member = mock_github_user
        claim.status = BoardCandidateClaim.Status.SUBMITTED
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimMutations()
        result = mutation.submit_board_candidate_claim(info, input_data)

        assert not result.ok
        assert result.code == "INVALID_STATUS"


class TestWithdrawBoardCandidateClaim:
    """Tests for withdraw_board_candidate_claim mutation."""

    def _make_input_data(self, key, withdrawn_reason="No longer relevant", year=2025):
        return MagicMock(
            key=key,
            withdrawn_reason=withdrawn_reason,
            year=year,
        )

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.timezone")
    def test_withdraw_claim_success_submitted(self, mock_timezone, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data("test-key")
        now = datetime(2024, 1, 1, tzinfo=UTC)
        mock_timezone.now.return_value = now

        claim = MagicMock()
        claim.candidate.member = mock_github_user
        claim.status = BoardCandidateClaim.Status.SUBMITTED
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimMutations()
        result = mutation.withdraw_board_candidate_claim(info, input_data)

        assert result.ok
        assert result.code == "SUCCESS"
        assert result.claim is claim
        assert claim.status == BoardCandidateClaim.Status.WITHDRAWN
        assert claim.withdrawn_reason == "No longer relevant"
        assert claim.withdrawn_at == now
        claim.save.assert_called_once()

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.timezone")
    def test_withdraw_claim_success_approved(self, mock_timezone, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data("test-key")
        now = datetime(2024, 1, 1, tzinfo=UTC)
        mock_timezone.now.return_value = now

        claim = MagicMock()
        claim.candidate.member = mock_github_user
        claim.status = BoardCandidateClaim.Status.APPROVED
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimMutations()
        result = mutation.withdraw_board_candidate_claim(info, input_data)

        assert result.ok
        assert result.code == "SUCCESS"
        assert result.claim is claim
        assert claim.status == BoardCandidateClaim.Status.WITHDRAWN
        assert claim.withdrawn_reason == "No longer relevant"
        assert claim.withdrawn_at == now

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_withdraw_claim_invalid_status(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data("test-key")

        claim = MagicMock()
        claim.candidate.member = mock_github_user
        claim.status = BoardCandidateClaim.Status.DRAFT
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimMutations()
        result = mutation.withdraw_board_candidate_claim(info, input_data)

        assert not result.ok
        assert result.code == "INVALID_STATUS"


class TestValidateReorderClaims:
    """Tests for _validate_reorder_claims helper."""

    def _make_input_data(self, keys, year=2025):
        return MagicMock(keys=list(keys), year=year)

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_validate_success(self, mock_claim_model):
        login = "alice"
        input_data = self._make_input_data(["k1", "k2", "k3"])
        mock_claim_model.objects.filter.return_value.count.return_value = 3

        keys, error = _validate_reorder_claims(login, input_data)

        mock_claim_model.objects.filter.assert_called_once_with(
            candidate__member__login=login, key__in=["k1", "k2", "k3"], board__year=input_data.year
        )
        assert keys == ["k1", "k2", "k3"]
        assert error is None

    def test_validate_empty_input(self):
        login = "alice"
        input_data = self._make_input_data([])

        keys, error = _validate_reorder_claims(login, input_data)

        assert keys == []
        assert error is not None
        assert not error.ok
        assert error.code == "VALIDATION_ERROR"

    def test_validate_duplicate_keys(self):
        login = "alice"
        input_data = self._make_input_data(["k1", "k1", "k2"])

        keys, error = _validate_reorder_claims(login, input_data)

        assert keys == ["k1", "k1", "k2"]
        assert error is not None
        assert not error.ok
        assert error.code == "VALIDATION_ERROR"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_validate_missing_keys(self, mock_claim_model):
        login = "alice"
        input_data = self._make_input_data(["k1", "k2"])
        mock_claim_model.objects.filter.return_value.count.return_value = 1

        keys, error = _validate_reorder_claims(login, input_data)

        assert keys == ["k1", "k2"]
        assert error is not None
        assert not error.ok
        assert error.code == "NOT_FOUND"


class TestReorderBoardCandidateClaims:
    """Tests for reorder_board_candidate_claims mutation."""

    def _make_input_data(self, keys, year=2025):
        return MagicMock(keys=list(keys), year=year)

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_reorder_claims_success(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data(["k2", "k1", "k3"])

        claim_a = MagicMock(id=1, key="k1", status=BoardCandidateClaim.Status.APPROVED)
        claim_a.candidate.member = mock_github_user
        claim_a.candidate_id = 10
        claim_a.board_id = 20
        claim_b = MagicMock(id=2, key="k2", status=BoardCandidateClaim.Status.APPROVED)
        claim_b.candidate.member = mock_github_user
        claim_b.candidate_id = 10
        claim_b.board_id = 20
        claim_c = MagicMock(id=3, key="k3", status=BoardCandidateClaim.Status.APPROVED)
        claim_c.candidate.member = mock_github_user
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
        user.is_authenticated = True
        info = _make_info(user)
        input_data = self._make_input_data([])

        mutation = BoardCandidateClaimMutations()
        result = mutation.reorder_board_candidate_claims(info, input_data)

        assert not result.ok
        assert result.code == "VALIDATION_ERROR"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_reorder_claims_duplicate_keys(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        info = _make_info(user)
        input_data = self._make_input_data(["k1", "k1", "k2"])

        mutation = BoardCandidateClaimMutations()
        result = mutation.reorder_board_candidate_claims(info, input_data)

        assert not result.ok
        assert result.code == "VALIDATION_ERROR"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_reorder_claims_missing_keys(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        info = _make_info(user)
        input_data = self._make_input_data(["k1", "k2"])

        mock_claim_model.objects.filter.return_value.count.return_value = 1

        mutation = BoardCandidateClaimMutations()
        result = mutation.reorder_board_candidate_claims(info, input_data)

        assert not result.ok
        assert result.code == "NOT_FOUND"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_reorder_claims_mixed_candidates(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data(["k1", "k2"])

        claim_a = MagicMock(id=1, key="k1")
        claim_a.candidate.member = mock_github_user
        claim_a.candidate_id = 10
        claim_a.board_id = 20
        claim_b = MagicMock(id=2, key="k2")
        claim_b.candidate.member = mock_github_user
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
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data(["k1", "k2"])

        claim_a = MagicMock(id=1, key="k1", status=BoardCandidateClaim.Status.DRAFT)
        claim_a.candidate.member = mock_github_user
        claim_a.candidate_id = 10
        claim_a.board_id = 20
        claim_b = MagicMock(id=2, key="k2", status=BoardCandidateClaim.Status.DRAFT)
        claim_b.candidate.member = mock_github_user
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
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data(["k1", "k2"])

        claim_a = MagicMock(id=1, key="k1")
        claim_a.candidate.member = mock_github_user
        claim_a.candidate_id = 10
        claim_a.board_id = 20
        claim_b = MagicMock(id=2, key="k2")
        claim_b.candidate.member = mock_github_user
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


class TestCreateBoardCandidateClaim:
    """Tests for create_board_candidate_claim mutation."""

    def _make_input_data(self, name="Test Claim", description="Test description", year=2025):
        data = MagicMock()
        data.name = name
        data.description = description
        data.year = year
        return data

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardOfDirectors")
    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_create_claim_success(self, mock_claim_model, mock_board_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data()

        mock_board = MagicMock()
        mock_candidate = MagicMock()
        mock_board.get_candidate.return_value = mock_candidate
        mock_board_model.objects.get.return_value = mock_board

        mutation = BoardCandidateClaimMutations()
        result = mutation.create_board_candidate_claim(info, input_data)

        mock_board_model.objects.get.assert_called_once_with(year=2025)
        mock_board.get_candidate.assert_called_once_with(login=mock_github_user.login)
        mock_claim_model.objects.create.assert_called_once_with(
            board=mock_board,
            candidate=mock_candidate,
            description=input_data.description,
            name=input_data.name,
        )
        assert result.ok
        assert result.code == "SUCCESS"
        assert result.claim is not None

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardOfDirectors")
    def test_create_claim_board_not_found(self, mock_board_model):
        mock_board_model.DoesNotExist = BoardOfDirectors.DoesNotExist
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data(year=2099)

        mock_board_model.objects.get.side_effect = BoardOfDirectors.DoesNotExist

        mutation = BoardCandidateClaimMutations()
        result = mutation.create_board_candidate_claim(info, input_data)

        assert not result.ok
        assert result.code == "NOT_FOUND"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardOfDirectors")
    def test_create_claim_no_github_user(self, mock_board_model):
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = None
        info = _make_info(user)
        input_data = self._make_input_data()

        mock_board = MagicMock()
        mock_board_model.objects.get.return_value = mock_board

        mutation = BoardCandidateClaimMutations()
        result = mutation.create_board_candidate_claim(info, input_data)

        assert not result.ok
        assert result.code == "FORBIDDEN"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardOfDirectors")
    def test_create_claim_not_a_candidate(self, mock_board_model):
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data()

        mock_board = MagicMock()
        mock_board.get_candidate.return_value = None
        mock_board_model.objects.get.return_value = mock_board

        mutation = BoardCandidateClaimMutations()
        result = mutation.create_board_candidate_claim(info, input_data)

        assert not result.ok
        assert result.code == "FORBIDDEN"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardOfDirectors")
    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_create_claim_integrity_error(self, mock_claim_model, mock_board_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data()

        mock_board = MagicMock()
        mock_candidate = MagicMock()
        mock_board.get_candidate.return_value = mock_candidate
        mock_board_model.objects.get.return_value = mock_board

        mock_claim_model.objects.create.side_effect = IntegrityError

        mutation = BoardCandidateClaimMutations()
        result = mutation.create_board_candidate_claim(info, input_data)

        assert not result.ok
        assert result.code == "ERROR"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardOfDirectors")
    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_create_claim_validation_error(self, mock_claim_model, mock_board_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data()

        mock_board = MagicMock()
        mock_candidate = MagicMock()
        mock_board.get_candidate.return_value = mock_candidate
        mock_board_model.objects.get.return_value = mock_board

        mock_claim_model.objects.create.side_effect = ValidationError(
            {"description": ["This field is required."]}
        )

        mutation = BoardCandidateClaimMutations()
        result = mutation.create_board_candidate_claim(info, input_data)

        assert not result.ok
        assert result.code == "VALIDATION_ERROR"
        assert "required" in result.message


class TestUpdateBoardCandidateClaim:
    """Tests for update_board_candidate_claim mutation."""

    def _make_input_data(
        self, key="test-key", name="Updated Claim", description="Updated description", year=2025
    ):
        data = MagicMock()
        data.key = key
        data.name = name
        data.description = description
        data.year = year
        return data

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_update_claim_success(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data()

        claim = MagicMock()
        claim.candidate.member = mock_github_user
        claim.is_locked = False
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimMutations()
        result = mutation.update_board_candidate_claim(info, input_data)

        assert result.ok
        assert result.code == "SUCCESS"
        assert result.claim is claim
        assert claim.name == input_data.name
        assert claim.description == input_data.description
        claim.save.assert_called_once()

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_update_claim_partial(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = MagicMock(key="test-key", description=None, year=2025)
        input_data.name = "Updated Name"

        claim = MagicMock()
        claim.candidate.member = mock_github_user
        claim.is_locked = False
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimMutations()
        result = mutation.update_board_candidate_claim(info, input_data)

        assert result.ok
        assert result.code == "SUCCESS"
        assert result.claim is claim
        assert claim.name == "Updated Name"
        claim.save.assert_called_once_with(update_fields=["name", "key"])

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_update_claim_not_found(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        mock_claim_model.DoesNotExist = BoardCandidateClaim.DoesNotExist
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data(key="non-existent")

        mock_claim_model.objects.select_for_update.return_value.get.side_effect = (
            BoardCandidateClaim.DoesNotExist
        )

        mutation = BoardCandidateClaimMutations()
        result = mutation.update_board_candidate_claim(info, input_data)

        assert not result.ok
        assert result.code == "NOT_FOUND"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_update_claim_locked(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data()

        claim = MagicMock()
        claim.candidate.member = mock_github_user
        claim.is_locked = True
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimMutations()
        result = mutation.update_board_candidate_claim(info, input_data)

        assert not result.ok
        assert result.code == "LOCKED"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_update_claim_integrity_error(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data()

        claim = MagicMock()
        claim.candidate.member = mock_github_user
        claim.is_locked = False
        claim.save.side_effect = IntegrityError
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimMutations()
        result = mutation.update_board_candidate_claim(info, input_data)

        assert not result.ok
        assert result.code == "ERROR"

    @patch("apps.owasp.api.internal.mutations.board_candidate_claim.BoardCandidateClaim")
    def test_update_claim_validation_error(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = self._make_input_data()

        claim = MagicMock()
        claim.candidate.member = mock_github_user
        claim.is_locked = False
        claim.save.side_effect = ValidationError({"name": ["Invalid."]})
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimMutations()
        result = mutation.update_board_candidate_claim(info, input_data)

        assert not result.ok
        assert result.code == "VALIDATION_ERROR"
