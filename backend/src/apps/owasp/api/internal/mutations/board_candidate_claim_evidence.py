"""OWASP Board Candidate Claim Evidence GraphQL mutations."""

import logging

import pydantic
import strawberry
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils import timezone
from strawberry.file_uploads import Upload
from strawberry.types import Info

from apps.common.api.internal.mutations.common import FieldError, validate_pydantic_input
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


class CreateEvidencePydanticInput(pydantic.BaseModel):
    """Pydantic validation for creating claim evidence."""

    claim_key: str = pydantic.Field(max_length=100)
    description: str
    name: str = pydantic.Field(max_length=200)
    source_url: pydantic.HttpUrl | None = None
    year: int


@strawberry.experimental.pydantic.input(model=CreateEvidencePydanticInput, all_fields=True)
class CreateEvidenceInput:
    """Input for creating claim evidence."""

    file: Upload | None = strawberry.field(default=None)


class UpdateEvidencePydanticInput(pydantic.BaseModel):
    """Pydantic validation for updating claim evidence."""

    claim_key: str = pydantic.Field(max_length=100)
    description: str | None = None
    key: str = pydantic.Field(max_length=100)
    name: str | None = pydantic.Field(default=None, max_length=200)
    source_url: pydantic.HttpUrl | None = None
    year: int


@strawberry.experimental.pydantic.input(model=UpdateEvidencePydanticInput, all_fields=True)
class UpdateEvidenceInput:
    """Input for updating claim evidence."""

    file: Upload | None = strawberry.field(default=None)


class RemoveEvidencePydanticInput(pydantic.BaseModel):
    """Pydantic validation for removing claim evidence."""

    claim_key: str = pydantic.Field(max_length=100)
    key: str = pydantic.Field(max_length=100)
    removed_reason: str | None = None
    year: int


@strawberry.experimental.pydantic.input(model=RemoveEvidencePydanticInput, all_fields=True)
class RemoveEvidenceInput:
    """Input for removing claim evidence."""


@strawberry.type
class EvidenceResult:
    """Result for claim evidence mutations."""

    ok: bool
    code: str | None = None
    message: str | None = None
    evidence: BoardCandidateClaimEvidenceNode | None = None
    field_errors: list[FieldError] | None = None


@strawberry.type
class BoardCandidateClaimEvidenceMutations:
    """Board Candidate Claim Evidence mutations."""

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    @validate_pydantic_input(EvidenceResult)
    def create_board_candidate_claim_evidence(
        self, info: Info, input_data: CreateEvidenceInput
    ) -> EvidenceResult:
        """Create evidence for a claim."""
        validated = input_data.validated_data  # type: ignore[attr-defined]
        user = info.context.request.user
        if user.github_user is None:
            return EvidenceResult(ok=False, code="FORBIDDEN", message=ACCESS_DENIED_MSG)

        try:
            claim = BoardCandidateClaim.objects.select_for_update().get(
                board__year=validated.year,
                candidate__member__login=user.github_user.login,
                key=validated.claim_key,
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
                description=validated.description,
                file=input_data.file,
                name=validated.name,
                source_url=str(validated.source_url) if validated.source_url else "",
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
            messages = []
            for msgs in e.message_dict.values():
                messages.extend(msgs)
            return EvidenceResult(
                ok=False,
                code="VALIDATION_ERROR",
                message=" ".join(messages),
            )

        return EvidenceResult(
            ok=True,
            code="SUCCESS",
            message="Evidence created successfully.",
            evidence=evidence,
        )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    @validate_pydantic_input(EvidenceResult)
    def update_board_candidate_claim_evidence(
        self, info: Info, input_data: UpdateEvidenceInput
    ) -> EvidenceResult:
        """Update evidence for a claim."""
        validated = input_data.validated_data  # type: ignore[attr-defined]
        user = info.context.request.user
        if user.github_user is None:
            return EvidenceResult(ok=False, code="FORBIDDEN", message=ACCESS_DENIED_MSG)

        try:
            evidence = BoardCandidateClaimEvidence.objects.select_for_update().get(
                claim__board__year=validated.year,
                claim__candidate__member__login=user.github_user.login,
                claim__key=validated.claim_key,
                key=validated.key,
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
        if validated.name is not None:
            evidence.name = validated.name
            update_fields.append("name")
            update_fields.append("key")
        if validated.description is not None:
            evidence.description = validated.description
            update_fields.append("description")
        evidence.source_url = str(validated.source_url) if validated.source_url else ""
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
            messages = []
            for msgs in e.message_dict.values():
                messages.extend(msgs)
            return EvidenceResult(
                ok=False,
                code="VALIDATION_ERROR",
                message=" ".join(messages),
            )

        return EvidenceResult(
            ok=True,
            code="SUCCESS",
            message="Evidence updated successfully.",
            evidence=evidence,
        )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    @validate_pydantic_input(EvidenceResult)
    def remove_board_candidate_claim_evidence(
        self, info: Info, input_data: RemoveEvidenceInput
    ) -> EvidenceResult:
        """Remove evidence for a claim."""
        validated = input_data.validated_data  # type: ignore[attr-defined]
        user = info.context.request.user
        if user.github_user is None:
            return EvidenceResult(ok=False, code="FORBIDDEN", message=ACCESS_DENIED_MSG)

        try:
            evidence = BoardCandidateClaimEvidence.objects.select_for_update().get(
                claim__board__year=validated.year,
                claim__candidate__member__login=user.github_user.login,
                claim__key=validated.claim_key,
                key=validated.key,
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
            old_file = evidence.file
            evidence.file = None
            evidence.is_removed = True
            evidence.removed_at = timezone.now()
            evidence.removed_reason = validated.removed_reason or ""
            evidence.save(update_fields=["file", "is_removed", "removed_reason", "removed_at"])
            if old_file:
                transaction.on_commit(lambda f=old_file: f.delete(save=False))
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
            messages = []
            for msgs in e.message_dict.values():
                messages.extend(msgs)
            return EvidenceResult(
                ok=False,
                code="VALIDATION_ERROR",
                message=" ".join(messages),
            )

        return EvidenceResult(
            ok=True,
            code="SUCCESS",
            message="Evidence removed successfully.",
            evidence=evidence,
        )
