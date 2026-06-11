"""OWASP Board Candidate Claim Evidence GraphQL mutations."""

import json
import logging

import strawberry
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils import timezone
from strawberry.file_uploads import Upload
from strawberry.types import Info

from apps.nest.api.internal.permissions import IsAuthenticated
from apps.owasp.api.internal.nodes.board_candidate_claim_evidence import (
    BoardCandidateClaimEvidenceNode,
)
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from apps.owasp.models.board_candidate_claim_evidence import BoardCandidateClaimEvidence

logger = logging.getLogger(__name__)

ACCESS_DENIED_MSG = "Access denied."
CLAIM_NOT_FOUND_MSG = "Claim not found."
EVIDENCE_NOT_FOUND_MSG = "Evidence not found."
GENERIC_ERROR_MSG = "Something went wrong."


@strawberry.input
class CreateEvidenceInput:
    """Input for creating claim evidence."""

    claim_key: str
    description: str | None = None
    file: Upload | None = None
    name: str
    source_url: str | None = None


@strawberry.input
class UpdateEvidenceInput:
    """Input for updating claim evidence."""

    description: str | None = None
    file: Upload | None = None
    key: str
    name: str | None = None
    source_url: str | None = None


@strawberry.input
class RemoveEvidenceInput:
    """Input for removing claim evidence."""

    key: str
    removed_reason: str


@strawberry.type
class EvidenceResult:
    """Result for claim evidence mutations."""

    ok: bool
    code: str | None = None
    message: str | None = None
    evidence: BoardCandidateClaimEvidenceNode | None = None


@strawberry.type
class BoardCandidateClaimEvidenceMutations:
    """Board Candidate Claim Evidence mutations."""

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def create_board_candidate_claim_evidence(
        self, info: Info, input_data: CreateEvidenceInput
    ) -> EvidenceResult:
        """Create evidence for a claim."""
        user = info.context.request.user

        try:
            claim = BoardCandidateClaim.objects.select_for_update().get(
                claim__candidate__member__login=user.github_user.login, key=input_data.claim_key
            )
        except BoardCandidateClaim.DoesNotExist:
            return EvidenceResult(ok=False, code="NOT_FOUND", message=CLAIM_NOT_FOUND_MSG)

        if claim.status != BoardCandidateClaim.Status.DRAFT:
            return EvidenceResult(
                ok=False,
                code="INVALID_STATUS",
                message="Evidence can only be added to draft claims.",
            )

        try:
            evidence = BoardCandidateClaimEvidence.objects.create(
                claim=claim,
                name=input_data.name,
                description=input_data.description or "",
                file=input_data.file,
                source_url=input_data.source_url or "",
            )
        except IntegrityError:
            logger.warning(
                "Error creating Board Candidate Claim Evidence for claim %s",
                claim.id,
            )
            return EvidenceResult(
                ok=False,
                code="ERROR",
                message=GENERIC_ERROR_MSG,
            )
        except ValidationError as e:
            return EvidenceResult(
                ok=False,
                code="VALIDATION_ERROR",
                message=json.dumps(e.message_dict),
            )

        return EvidenceResult(
            ok=True,
            code="SUCCESS",
            message="Evidence created successfully.",
            evidence=evidence,
        )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def update_board_candidate_claim_evidence(
        self, info: Info, input_data: UpdateEvidenceInput
    ) -> EvidenceResult:
        """Update evidence for a claim."""
        user = info.context.request.user

        try:
            evidence = BoardCandidateClaimEvidence.objects.select_for_update().get(
                claim__candidate__member__login=user.github_user.login, key=input_data.key
            )
        except BoardCandidateClaimEvidence.DoesNotExist:
            return EvidenceResult(ok=False, code="NOT_FOUND", message=EVIDENCE_NOT_FOUND_MSG)

        if evidence.claim.status != BoardCandidateClaim.Status.DRAFT:
            return EvidenceResult(
                ok=False,
                code="INVALID_STATUS",
                message="Evidence can only be updated on draft claims.",
            )

        update_fields = []
        if input_data.name is not None:
            evidence.name = input_data.name
            update_fields.append("name")
        if input_data.description is not None:
            evidence.description = input_data.description
            update_fields.append("description")
        if input_data.source_url is not None:
            evidence.source_url = input_data.source_url
            update_fields.append("source_url")
        if input_data.file is not None:
            evidence.file = input_data.file
            update_fields.extend(["file", "file_name", "file_size"])

        try:
            evidence.save(update_fields=update_fields)
        except IntegrityError:
            logger.warning(
                "Error updating Board Candidate Claim Evidence %s",
                evidence.id,
            )
            return EvidenceResult(
                ok=False,
                code="ERROR",
                message=GENERIC_ERROR_MSG,
            )
        except ValidationError as e:
            return EvidenceResult(
                ok=False,
                code="VALIDATION_ERROR",
                message=json.dumps(e.message_dict),
            )

        return EvidenceResult(
            ok=True,
            code="SUCCESS",
            message="Evidence updated successfully.",
            evidence=evidence,
        )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def remove_board_candidate_claim_evidence(
        self, info: Info, input_data: RemoveEvidenceInput
    ) -> EvidenceResult:
        """Remove evidence for a claim."""
        user = info.context.request.user

        try:
            evidence = BoardCandidateClaimEvidence.objects.select_for_update().get(
                candidate__member__login=user.github_user.login, key=input_data.key
            )
        except BoardCandidateClaimEvidence.DoesNotExist:
            return EvidenceResult(ok=False, code="NOT_FOUND", message=EVIDENCE_NOT_FOUND_MSG)

        if evidence.claim.status not in BoardCandidateClaimEvidence.REMOVAL_ALLOWED_STATUSES:
            return EvidenceResult(
                ok=False,
                code="INVALID_STATUS",
                message="Evidence can only be removed from discarded, draft or withdrawn claims.",
            )

        try:
            evidence.is_removed = True
            evidence.removed_reason = input_data.removed_reason
            evidence.removed_at = timezone.now()
            evidence.save(update_fields=["is_removed", "removed_reason", "removed_at"])
        except IntegrityError:
            logger.warning(
                "Error removing Board Candidate Claim Evidence %s",
                evidence.id,
            )
            return EvidenceResult(
                ok=False,
                code="ERROR",
                message=GENERIC_ERROR_MSG,
            )
        except ValidationError as e:
            return EvidenceResult(
                ok=False,
                code="VALIDATION_ERROR",
                message=json.dumps(e.message_dict),
            )

        return EvidenceResult(
            ok=True,
            code="SUCCESS",
            message="Evidence removed successfully.",
            evidence=evidence,
        )
