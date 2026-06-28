"""Tests for BoardCandidateClaimReview mutations."""

from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from apps.owasp.api.internal.mutations.board_candidate_claim_review import (
    BoardCandidateClaimReviewMutations,
)
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from apps.owasp.models.board_candidate_claim_review import BoardCandidateClaimReview


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


def _make_input_data(
    claim_key="test-claim",
    claim_member_login="alice",
    decision="APPROVED",
    year=2025,
    notes="",
):
    data = MagicMock()
    data.claim_key = claim_key
    data.claim_member_login = claim_member_login
    data.decision = MagicMock()
    data.decision.value = decision
    data.year = year
    data.notes = notes
    return data


class TestCreateBoardCandidateClaimReview:
    """Tests for create_board_candidate_claim_review mutation."""

    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_review.BoardCandidateClaimReview"
    )
    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_review.BoardCandidateClaim")
    def test_create_review_success(self, mock_claim_model, mock_review_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        mock_review_model.DoesNotExist = BoardCandidateClaimReview.DoesNotExist
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        mock_github_user.is_owasp_staff = True
        mock_github_user.is_claim_reviewer = False
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = _make_input_data()

        claim = MagicMock()
        claim.status = BoardCandidateClaim.Status.SUBMITTED
        claim.board = MagicMock()
        claim.board.get_candidate.return_value = None
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mock_review = MagicMock()
        mock_review_model.objects.filter.return_value.exists.return_value = False
        mock_review_model.objects.create.return_value = mock_review

        mutation = BoardCandidateClaimReviewMutations()
        result = mutation.create_board_candidate_claim_review(info, input_data)

        assert result.ok
        assert result.code == "SUCCESS"
        assert result.review is mock_review
        mock_claim_model.objects.select_for_update.assert_called_once()
        mock_claim_model.objects.select_for_update.return_value.get.assert_called_once_with(
            board__year=2025,
            candidate__member__login="alice",
            key="test-claim",
        )
        mock_review_model.objects.create.assert_called_once_with(
            claim=claim,
            decision="APPROVED",
            notes="",
            reviewer=mock_github_user,
        )

    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_review.BoardCandidateClaimReview"
    )
    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_review.BoardCandidateClaim")
    def test_create_review_forbidden_no_github_user(self, mock_claim_model, mock_review_model):
        user = MagicMock()
        user.is_authenticated = True
        user.github_user = None
        info = _make_info(user)
        input_data = _make_input_data()

        mutation = BoardCandidateClaimReviewMutations()
        result = mutation.create_board_candidate_claim_review(info, input_data)

        assert not result.ok
        assert result.code == "FORBIDDEN"
        mock_claim_model.objects.select_for_update.assert_not_called()

    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_review.BoardCandidateClaimReview"
    )
    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_review.BoardCandidateClaim")
    def test_create_review_forbidden_not_reviewer(self, mock_claim_model, mock_review_model):
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        mock_github_user.is_owasp_staff = False
        mock_github_user.is_claim_reviewer = False
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = _make_input_data()

        mutation = BoardCandidateClaimReviewMutations()
        result = mutation.create_board_candidate_claim_review(info, input_data)

        assert not result.ok
        assert result.code == "FORBIDDEN"
        mock_claim_model.objects.select_for_update.assert_not_called()

    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_review.BoardCandidateClaimReview"
    )
    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_review.BoardCandidateClaim")
    def test_create_review_claim_not_found(self, mock_claim_model, mock_review_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        mock_claim_model.DoesNotExist = BoardCandidateClaim.DoesNotExist
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        mock_github_user.is_owasp_staff = True
        mock_github_user.is_claim_reviewer = False
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = _make_input_data()

        mock_claim_model.objects.select_for_update.return_value.get.side_effect = (
            BoardCandidateClaim.DoesNotExist
        )

        mutation = BoardCandidateClaimReviewMutations()
        result = mutation.create_board_candidate_claim_review(info, input_data)

        assert not result.ok
        assert result.code == "NOT_FOUND"

    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_review.BoardCandidateClaimReview"
    )
    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_review.BoardCandidateClaim")
    def test_create_review_invalid_status(self, mock_claim_model, mock_review_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        mock_github_user.is_owasp_staff = True
        mock_github_user.is_claim_reviewer = False
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = _make_input_data()

        claim = MagicMock()
        claim.status = BoardCandidateClaim.Status.DRAFT
        claim.board = MagicMock()
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimReviewMutations()
        result = mutation.create_board_candidate_claim_review(info, input_data)

        assert not result.ok
        assert result.code == "INVALID_STATUS"

    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_review.BoardCandidateClaimReview"
    )
    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_review.BoardCandidateClaim")
    def test_create_review_candidate_reviewer(self, mock_claim_model, mock_review_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        mock_github_user.is_owasp_staff = True
        mock_github_user.is_claim_reviewer = False
        mock_github_user.login = "reviewer"
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = _make_input_data()

        claim = MagicMock()
        claim.status = BoardCandidateClaim.Status.SUBMITTED
        claim.board = MagicMock()
        claim.board.get_candidate.return_value = MagicMock()
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mutation = BoardCandidateClaimReviewMutations()
        result = mutation.create_board_candidate_claim_review(info, input_data)

        assert not result.ok
        assert result.code == "FORBIDDEN"
        claim.board.get_candidate.assert_called_once_with(login="reviewer")

    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_review.BoardCandidateClaimReview"
    )
    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_review.BoardCandidateClaim")
    def test_create_review_duplicate(self, mock_claim_model, mock_review_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        mock_github_user.is_owasp_staff = True
        mock_github_user.is_claim_reviewer = False
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = _make_input_data()

        claim = MagicMock()
        claim.status = BoardCandidateClaim.Status.SUBMITTED
        claim.board = MagicMock()
        claim.board.get_candidate.return_value = None
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mock_review_model.objects.filter.return_value.exists.return_value = True

        mutation = BoardCandidateClaimReviewMutations()
        result = mutation.create_board_candidate_claim_review(info, input_data)

        assert not result.ok
        assert result.code == "DUPLICATE_REVIEW"
        mock_review_model.objects.filter.assert_called_once_with(
            claim=claim, reviewer=mock_github_user
        )
        mock_review_model.objects.create.assert_not_called()

    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_review.BoardCandidateClaimReview"
    )
    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_review.BoardCandidateClaim")
    def test_create_review_integrity_error(self, mock_claim_model, mock_review_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        mock_review_model.DoesNotExist = BoardCandidateClaimReview.DoesNotExist
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        mock_github_user.is_owasp_staff = True
        mock_github_user.is_claim_reviewer = False
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = _make_input_data()

        claim = MagicMock()
        claim.status = BoardCandidateClaim.Status.SUBMITTED
        claim.board = MagicMock()
        claim.board.get_candidate.return_value = None
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mock_review_model.objects.filter.return_value.exists.return_value = False
        mock_review_model.objects.create.side_effect = IntegrityError

        mutation = BoardCandidateClaimReviewMutations()
        result = mutation.create_board_candidate_claim_review(info, input_data)

        assert not result.ok
        assert result.code == "ERROR"

    @patch(
        "apps.owasp.api.internal.mutations.board_candidate_claim_review.BoardCandidateClaimReview"
    )
    @patch("apps.owasp.api.internal.mutations.board_candidate_claim_review.BoardCandidateClaim")
    def test_create_review_validation_error(self, mock_claim_model, mock_review_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        mock_review_model.DoesNotExist = BoardCandidateClaimReview.DoesNotExist
        user = MagicMock()
        user.is_authenticated = True
        mock_github_user = MagicMock()
        mock_github_user.is_owasp_staff = True
        mock_github_user.is_claim_reviewer = False
        user.github_user = mock_github_user
        info = _make_info(user)
        input_data = _make_input_data()

        claim = MagicMock()
        claim.status = BoardCandidateClaim.Status.SUBMITTED
        claim.board = MagicMock()
        claim.board.get_candidate.return_value = None
        mock_claim_model.objects.select_for_update.return_value.get.return_value = claim

        mock_review_model.objects.filter.return_value.exists.return_value = False
        mock_review_model.objects.create.side_effect = ValidationError(
            {"notes": ["Invalid notes."]}
        )

        mutation = BoardCandidateClaimReviewMutations()
        result = mutation.create_board_candidate_claim_review(info, input_data)

        assert not result.ok
        assert result.code == "VALIDATION_ERROR"
