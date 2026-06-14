"""OWASP Board Candidate Claim Evidence GraphQL queries."""

import strawberry
import strawberry_django

from apps.owasp.api.internal.nodes.board_candidate_claim_evidence import (
    BoardCandidateClaimEvidenceNode,
)
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from apps.owasp.models.board_candidate_claim_evidence import BoardCandidateClaimEvidence


@strawberry.type
class BoardCandidateClaimEvidenceQuery:
    """GraphQL queries for Board Candidate Claim Evidence model."""

    @strawberry_django.field
    def board_candidate_claim_evidences(
        self, info: strawberry.Info, claim_key: str, login: str, year: int
    ) -> list[BoardCandidateClaimEvidenceNode]:
        """Resolve Board Candidate Claim Evidences for a given claim.

        Args:
            info (Info): Strawberry Info.
            claim_key (str): The key of the claim.
            login (str): The login of the candidate.
            year (int): The year of the election.

        Returns:
            List of BoardCandidateClaimEvidenceNode objects

        """
        user = info.context.request.user
        claim = BoardCandidateClaim.objects.filter(
            candidate__member__login=login, key=claim_key, board__year=year
        ).first()
        if claim is None:
            return []

        is_self = (
            user.is_authenticated
            and claim.candidate.member is not None
            and user.github_user == claim.candidate.member
        )

        return (
            claim.evidences.filter(is_removed=False)
            if is_self or claim.status == BoardCandidateClaim.Status.APPROVED
            else []
        )

    @strawberry_django.field
    def board_candidate_claim_evidence(
        self, info: strawberry.Info, claim_key: str, key: str, login: str, year: int
    ) -> BoardCandidateClaimEvidenceNode | None:
        """Resolve Board Candidate Claim Evidence for a given claim.

        Args:
            info (Info): Strawberry Info.
            claim_key (str): The key of the claim.
            key (str): The key of the evidence.
            login (str): The login of the candidate.
            year (int): The year of the election.

        Returns:
            BoardCandidateClaimEvidenceNode if found, None otherwise

        """
        user = info.context.request.user
        try:
            evidence = BoardCandidateClaimEvidence.objects.get(
                claim__key=claim_key,
                key=key,
                claim__candidate__member__login=login,
                claim__board__year=year,
                is_removed=False,
            )
        except BoardCandidateClaimEvidence.DoesNotExist:
            return None

        is_self = (
            user.is_authenticated
            and evidence.claim.candidate.member is not None
            and user.github_user == evidence.claim.candidate.member
        )

        return (
            evidence
            if is_self or evidence.claim.status == BoardCandidateClaim.Status.APPROVED
            else None
        )

    @strawberry_django.field
    def board_candidate_claim_evidence_file_url(
        self, info: strawberry.Info, claim_key: str, key: str, login: str, year: int
    ) -> str | None:
        """Resolve Board Candidate Claim Evidence file URL for a given claim.

        Args:
            info (Info): Strawberry Info.
            claim_key (str): The key of the claim.
            key (str): The key of the evidence.
            login (str): The login of the candidate.
            year (int): The year of the election.

        Returns:
            str: Evidence file URL if found, None otherwise

        """
        user = info.context.request.user
        try:
            evidence = BoardCandidateClaimEvidence.objects.get(
                claim__key=claim_key,
                key=key,
                claim__candidate__member__login=login,
                claim__board__year=year,
                is_removed=False,
            )
        except BoardCandidateClaimEvidence.DoesNotExist:
            return None

        is_self = (
            user.is_authenticated
            and evidence.claim.candidate.member is not None
            and user.github_user == evidence.claim.candidate.member
        )

        return (
            info.context.request.build_absolute_uri(evidence.file.url)
            if (is_self or evidence.claim.status == BoardCandidateClaim.Status.APPROVED)
            and evidence.file
            else None
        )
