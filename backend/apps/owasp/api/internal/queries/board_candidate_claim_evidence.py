"""OWASP Board Candidate Claim Evidence GraphQL queries."""

import strawberry
import strawberry_django

from apps.owasp.api.internal.nodes.board_candidate_claim_evidence import (
    BoardCandidateClaimEvidenceNode,
)
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from apps.owasp.models.board_candidate_claim_evidence import BoardCandidateClaimEvidence


def get_claim_evidence(
    info: strawberry.Info, claim_key: str, key: str, login: str, year: int
) -> BoardCandidateClaimEvidenceNode | None:
    """Resolve Board Candidate Claim Evidence.

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
            claim__board__year=year,
            claim__candidate__member__login=login,
            claim__key=claim_key,
            is_removed=False,
            key=key,
        )
    except BoardCandidateClaimEvidence.DoesNotExist:
        return None

    is_self = (
        user.is_authenticated
        and evidence.claim.candidate.member is not None
        and user.github_user == evidence.claim.candidate.member
    )
    is_reviewer = (
        user.is_authenticated
        and user.github_user is not None
        and (user.github_user.is_claim_reviewer or user.github_user.is_owasp_staff)
    )

    return (
        evidence
        if (
            is_self
            or (is_reviewer and evidence.claim.status == BoardCandidateClaim.Status.SUBMITTED)
            or evidence.claim.status == BoardCandidateClaim.Status.APPROVED
        )
        else None
    )


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
            board__year=year,
            candidate__member__login=login,
            key=claim_key,
        ).first()
        if claim is None:
            return []

        is_self = (
            user.is_authenticated
            and claim.candidate.member is not None
            and user.github_user == claim.candidate.member
        )
        is_reviewer = (
            user.is_authenticated
            and user.github_user is not None
            and (user.github_user.is_claim_reviewer or user.github_user.is_owasp_staff)
        )

        return (
            claim.evidences.filter(is_removed=False)
            if (
                is_self
                or (is_reviewer and claim.status == BoardCandidateClaim.Status.SUBMITTED)
                or claim.status == BoardCandidateClaim.Status.APPROVED
            )
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
        return get_claim_evidence(info, claim_key, key, login, year)

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
        evidence = get_claim_evidence(info, claim_key, key, login, year)

        return (
            info.context.request.build_absolute_uri(evidence.file.url)
            if evidence and evidence.file
            else None
        )
