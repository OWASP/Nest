"""Signal handlers for BoardCandidateClaimReview model."""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from apps.owasp.models.board_candidate_claim_review import BoardCandidateClaimReview

logger = logging.getLogger(__name__)


@receiver(post_save, sender=BoardCandidateClaimReview)
def review_post_save_finalize_claim_decision(sender, instance, **kwargs):  # noqa: ARG001
    """Signal handler to finalize a claim."""
    claim = instance.claim

    if claim.status != BoardCandidateClaim.Status.SUBMITTED:
        return

    threshold = claim.board.reviews_threshold
    approved_count = claim.reviews.filter(
        decision=BoardCandidateClaimReview.Decision.APPROVED,
    ).count()

    if approved_count >= threshold:
        claim.status = BoardCandidateClaim.Status.APPROVED
        claim.is_locked = True
        claim.save(update_fields=["is_locked", "status"])
        logger.info(
            "Claim '%s' auto-approved with %d approvals (threshold: %d).",
            claim.key,
            approved_count,
            threshold,
        )
