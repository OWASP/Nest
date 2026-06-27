"""Signal handlers for BoardOfDirectors model."""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from apps.owasp.models.board_candidate_claim_review import BoardCandidateClaimReview
from apps.owasp.models.board_of_directors import BoardOfDirectors

logger = logging.getLogger(__name__)


@receiver(post_save, sender=BoardOfDirectors)
def board_post_save_re_evaluate_claims(sender, instance, **kwargs):  # noqa: ARG001
    """Signal handler to re-evaluate claims when the threshold changes."""
    threshold = instance.reviews_threshold
    claims_to_approve = []

    for claim in instance.claims.filter(status=BoardCandidateClaim.Status.SUBMITTED):
        approved_count = claim.reviews.filter(
            decision=BoardCandidateClaimReview.Decision.APPROVED,
        ).count()

        if approved_count >= threshold:
            claim.status = BoardCandidateClaim.Status.APPROVED
            claim.is_locked = True
            claims_to_approve.append(claim)

    if claims_to_approve:
        BoardCandidateClaim.objects.bulk_update(claims_to_approve, ["is_locked", "status"])
        logger.info(
            "Approved %d claims after threshold change on board %d.",
            len(claims_to_approve),
            instance.year,
        )
