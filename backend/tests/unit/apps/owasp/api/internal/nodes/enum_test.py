"""Tests for OWASP GraphQL enums."""

from apps.owasp.api.internal.nodes.enum import ClaimStatusEnum
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim


class TestClaimStatusEnum:
    """Tests for ClaimStatusEnum values."""

    def test_claim_status_enum_values(self):
        """Test that ClaimStatusEnum maps correctly to model choices."""
        assert ClaimStatusEnum.DRAFT.value == BoardCandidateClaim.Status.DRAFT
        assert ClaimStatusEnum.DISCARDED.value == BoardCandidateClaim.Status.DISCARDED
        assert ClaimStatusEnum.SUBMITTED.value == BoardCandidateClaim.Status.SUBMITTED
        assert ClaimStatusEnum.APPROVED.value == BoardCandidateClaim.Status.APPROVED
        assert ClaimStatusEnum.REJECTED.value == BoardCandidateClaim.Status.REJECTED
        assert ClaimStatusEnum.WITHDRAWN.value == BoardCandidateClaim.Status.WITHDRAWN
