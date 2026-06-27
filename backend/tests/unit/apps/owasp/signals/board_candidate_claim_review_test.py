"""Tests for BoardCandidateClaimReview signal handler."""

from unittest.mock import MagicMock, patch

from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from apps.owasp.models.board_candidate_claim_review import BoardCandidateClaimReview
from apps.owasp.signals.board_candidate_claim_review import (
    review_post_save_finalize_claim_decision,
)


class TestReviewPostSaveFinalizeClaimDecision:
    """Tests for review_post_save_finalize_claim_decision signal."""

    @patch("apps.owasp.signals.board_candidate_claim_review.logger")
    def test_auto_approves_when_threshold_met(self, mock_logger):
        claim = MagicMock(spec=BoardCandidateClaim)
        claim.status = BoardCandidateClaim.Status.SUBMITTED
        claim.key = "test-claim"
        claim.board = MagicMock()
        claim.board.reviews_threshold = 2
        claim.reviews.filter.return_value.count.return_value = 2

        instance = MagicMock(spec=BoardCandidateClaimReview)
        instance.claim = claim

        review_post_save_finalize_claim_decision(sender=None, instance=instance)

        assert claim.status == BoardCandidateClaim.Status.APPROVED
        assert claim.is_locked is True
        claim.save.assert_called_once()
        mock_logger.info.assert_called_once_with(
            "Claim '%s' auto-approved with %d approvals (threshold: %d).",
            "test-claim",
            2,
            2,
        )

    @patch("apps.owasp.signals.board_candidate_claim_review.logger")
    def test_does_not_approve_when_threshold_not_met(self, mock_logger):
        claim = MagicMock(spec=BoardCandidateClaim)
        claim.status = BoardCandidateClaim.Status.SUBMITTED
        claim.board = MagicMock()
        claim.board.reviews_threshold = 3
        claim.reviews.filter.return_value.count.return_value = 2

        instance = MagicMock(spec=BoardCandidateClaimReview)
        instance.claim = claim

        review_post_save_finalize_claim_decision(sender=None, instance=instance)

        assert claim.status == BoardCandidateClaim.Status.SUBMITTED
        claim.save.assert_not_called()
        mock_logger.info.assert_not_called()

    @patch("apps.owasp.signals.board_candidate_claim_review.logger")
    def test_does_nothing_when_claim_not_submitted(self, mock_logger):
        claim = MagicMock(spec=BoardCandidateClaim)
        claim.status = BoardCandidateClaim.Status.DRAFT

        instance = MagicMock(spec=BoardCandidateClaimReview)
        instance.claim = claim

        review_post_save_finalize_claim_decision(sender=None, instance=instance)

        claim.save.assert_not_called()
        mock_logger.info.assert_not_called()

    @patch("apps.owasp.signals.board_candidate_claim_review.logger")
    def test_auto_approves_when_approvals_exactly_equal_threshold(self, mock_logger):
        claim = MagicMock(spec=BoardCandidateClaim)
        claim.status = BoardCandidateClaim.Status.SUBMITTED
        claim.key = "test-claim"
        claim.board = MagicMock()
        claim.board.reviews_threshold = 3
        claim.reviews.filter.return_value.count.return_value = 3

        instance = MagicMock(spec=BoardCandidateClaimReview)
        instance.claim = claim

        review_post_save_finalize_claim_decision(sender=None, instance=instance)

        assert claim.status == BoardCandidateClaim.Status.APPROVED
        assert claim.is_locked is True
        claim.save.assert_called_once()
        mock_logger.info.assert_called_once()
