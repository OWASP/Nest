"""OWASP Board Candidate Claim GraphQL mutations."""

import logging
from typing import Annotated

import pydantic
import strawberry
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils import timezone
from strawberry.types import Info

from apps.common.api.internal.mutations.common import FieldError, validate_pydantic_input
from apps.nest.api.internal.permissions import IsAuthenticated
from apps.owasp.api.internal.mutations.common import (
    MAX_KEY_LENGTH,
    MAX_NAME_LENGTH,
    MAX_REORDER_KEYS,
    MAX_TEXT_LENGTH,
    BaseInput,
    validate_slug,
    validate_year,
)
from apps.owasp.api.internal.nodes.board_candidate_claim import BoardCandidateClaimNode
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from apps.owasp.models.board_of_directors import BoardOfDirectors

logger = logging.getLogger(__name__)

ACCESS_DENIED_MSG = "Access denied."
CLAIM_NOT_FOUND_MSG = "Claim not found."
GENERIC_ERROR_MSG = "Something went wrong."


class CreateClaimPydanticInput(BaseInput):
    """Pydantic validation for creating a claim."""

    description: str = pydantic.Field(min_length=1, max_length=MAX_TEXT_LENGTH)
    name: str = pydantic.Field(min_length=1, max_length=MAX_NAME_LENGTH)
    source_text: str = pydantic.Field(default="", max_length=MAX_TEXT_LENGTH)
    year: int

    _validate_year = pydantic.field_validator("year")(validate_year)


@strawberry.experimental.pydantic.input(model=CreateClaimPydanticInput, all_fields=True)
class CreateClaimInput:
    """Input for creating a claim."""


class UpdateClaimPydanticInput(BaseInput):
    """Pydantic validation for updating a claim."""

    description: str | None = pydantic.Field(default=None, max_length=MAX_TEXT_LENGTH)
    key: str = pydantic.Field(max_length=MAX_KEY_LENGTH)
    name: str | None = pydantic.Field(default=None, min_length=1, max_length=MAX_NAME_LENGTH)
    source_text: str | None = pydantic.Field(default=None, max_length=MAX_TEXT_LENGTH)
    year: int

    _validate_key = pydantic.field_validator("key")(validate_slug)
    _validate_year = pydantic.field_validator("year")(validate_year)


@strawberry.experimental.pydantic.input(model=UpdateClaimPydanticInput, all_fields=True)
class UpdateClaimInput:
    """Input for updating a claim."""


class DiscardClaimPydanticInput(BaseInput):
    """Pydantic validation for discarding a claim."""

    key: str = pydantic.Field(max_length=MAX_KEY_LENGTH)
    year: int

    _validate_key = pydantic.field_validator("key")(validate_slug)
    _validate_year = pydantic.field_validator("year")(validate_year)


@strawberry.experimental.pydantic.input(model=DiscardClaimPydanticInput, all_fields=True)
class DiscardClaimInput:
    """Input for discarding a claim."""


class SubmitClaimPydanticInput(BaseInput):
    """Pydantic validation for submitting a claim."""

    key: str = pydantic.Field(max_length=MAX_KEY_LENGTH)
    year: int

    _validate_key = pydantic.field_validator("key")(validate_slug)
    _validate_year = pydantic.field_validator("year")(validate_year)


@strawberry.experimental.pydantic.input(model=SubmitClaimPydanticInput, all_fields=True)
class SubmitClaimInput:
    """Input for submitting a claim."""


class WithdrawClaimPydanticInput(BaseInput):
    """Pydantic validation for withdrawing a claim."""

    key: str = pydantic.Field(max_length=MAX_KEY_LENGTH)
    withdrawn_reason: str = pydantic.Field(default="", max_length=MAX_TEXT_LENGTH)
    year: int

    _validate_key = pydantic.field_validator("key")(validate_slug)
    _validate_year = pydantic.field_validator("year")(validate_year)


@strawberry.experimental.pydantic.input(model=WithdrawClaimPydanticInput, all_fields=True)
class WithdrawClaimInput:
    """Input for withdrawing a claim."""


class ReorderClaimsPydanticInput(BaseInput):
    """Pydantic validation for reordering claims."""

    keys: list[Annotated[str, pydantic.StringConstraints(max_length=MAX_KEY_LENGTH)]] = (
        pydantic.Field(min_length=1, max_length=MAX_REORDER_KEYS)
    )
    year: int

    _validate_year = pydantic.field_validator("year")(validate_year)

    @pydantic.field_validator("keys")
    @classmethod
    def keys_must_be_unique_slugs(cls, value: list[str]) -> list[str]:
        """Reject duplicate keys and keys that aren't valid slugs."""
        if len(set(value)) != len(value):
            message = "Duplicate claim keys are not allowed."
            raise ValueError(message)
        for key in value:
            validate_slug(key)
        return value


@strawberry.experimental.pydantic.input(model=ReorderClaimsPydanticInput, all_fields=True)
class ReorderClaimsInput:
    """Input for reordering claims."""


@strawberry.type
class ReorderClaimsResult:
    """Result for reorder claims mutation."""

    ok: bool
    code: str | None = None
    message: str | None = None
    claims: list[BoardCandidateClaimNode] | None = None
    field_errors: list[FieldError] | None = None


@strawberry.type
class ClaimResult:
    """Result for claim mutations."""

    ok: bool
    code: str | None = None
    message: str | None = None
    claim: BoardCandidateClaimNode | None = None
    field_errors: list[FieldError] | None = None


@strawberry.type
class BoardCandidateClaimMutations:
    """Board Candidate Claim mutations."""

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    @validate_pydantic_input(ClaimResult)
    def create_board_candidate_claim(
        self, info: Info, input_data: CreateClaimInput
    ) -> ClaimResult:
        """Create a new draft claim for a candidate."""
        validated = input_data.validated_data  # type: ignore[attr-defined]
        user = info.context.request.user
        if user.github_user is None:
            return ClaimResult(ok=False, code="FORBIDDEN", message=ACCESS_DENIED_MSG)

        try:
            board = BoardOfDirectors.objects.get(year=validated.year)
        except BoardOfDirectors.DoesNotExist:
            return ClaimResult(
                ok=False,
                code="NOT_FOUND",
                message=f"No board election found for the year {validated.year}.",
            )

        candidate = board.get_candidate(login=user.github_user.login)
        if not candidate:
            return ClaimResult(
                ok=False,
                code="FORBIDDEN",
                message="You are not registered as an active candidate for this election.",
            )

        try:
            claim = BoardCandidateClaim.objects.create(
                board=board,
                candidate=candidate,
                description=validated.description,
                name=validated.name,
                source_text=validated.source_text,
            )
        except IntegrityError:
            logger.warning(
                "Error creating Board Candidate Claim for candidate %s, year %s",
                candidate.member.login,
                validated.year,
            )
            return ClaimResult(
                ok=False,
                code="ERROR",
                message=GENERIC_ERROR_MSG,
            )
        except ValidationError as e:
            messages = []
            for msgs in e.message_dict.values():
                messages.extend(msgs)
            return ClaimResult(
                ok=False,
                code="VALIDATION_ERROR",
                message=" ".join(messages),
            )

        return ClaimResult(
            ok=True,
            code="SUCCESS",
            message="Claim created successfully.",
            claim=claim,
        )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    @validate_pydantic_input(ClaimResult)
    def update_board_candidate_claim(
        self, info: Info, input_data: UpdateClaimInput
    ) -> ClaimResult:
        """Update a draft claim."""
        validated = input_data.validated_data  # type: ignore[attr-defined]
        user = info.context.request.user
        if user.github_user is None:
            return ClaimResult(ok=False, code="FORBIDDEN", message=ACCESS_DENIED_MSG)

        try:
            claim = BoardCandidateClaim.objects.select_for_update().get(
                board__year=validated.year,
                candidate__member__login=user.github_user.login,
                key=validated.key,
            )
        except BoardCandidateClaim.DoesNotExist:
            return ClaimResult(ok=False, code="NOT_FOUND", message=CLAIM_NOT_FOUND_MSG)

        if claim.is_locked:
            return ClaimResult(ok=False, code="LOCKED", message="Cannot update a locked claim.")

        update_fields = []
        if validated.name:
            claim.name = validated.name
            update_fields.append("name")
            update_fields.append("key")
        if validated.description:
            claim.description = validated.description
            update_fields.append("description")
        if validated.source_text is not None:
            claim.source_text = validated.source_text
            update_fields.append("source_text")

        try:
            claim.save(update_fields=update_fields)
        except IntegrityError:
            logger.warning(
                "Error updating Board Candidate Claim for candidate %s, key %s",
                claim.candidate.member.login,
                validated.key,
            )
            return ClaimResult(
                ok=False,
                code="ERROR",
                message=GENERIC_ERROR_MSG,
            )
        except ValidationError as e:
            messages = []
            for msgs in e.message_dict.values():
                messages.extend(msgs)
            return ClaimResult(
                ok=False,
                code="VALIDATION_ERROR",
                message=" ".join(messages),
            )

        return ClaimResult(
            ok=True,
            code="SUCCESS",
            message="Claim updated successfully.",
            claim=claim,
        )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    @validate_pydantic_input(ClaimResult)
    def discard_board_candidate_claim(
        self, info: Info, input_data: DiscardClaimInput
    ) -> ClaimResult:
        """Discard a claim."""
        validated = input_data.validated_data  # type: ignore[attr-defined]
        user = info.context.request.user
        if user.github_user is None:
            return ClaimResult(ok=False, code="FORBIDDEN", message=ACCESS_DENIED_MSG)

        try:
            claim = BoardCandidateClaim.objects.select_for_update().get(
                board__year=validated.year,
                candidate__member__login=user.github_user.login,
                key=validated.key,
            )
        except BoardCandidateClaim.DoesNotExist:
            return ClaimResult(ok=False, code="NOT_FOUND", message=CLAIM_NOT_FOUND_MSG)

        if claim.status != BoardCandidateClaim.Status.DRAFT:
            return ClaimResult(
                ok=False,
                code="INVALID_STATUS",
                message="Only draft claims can be discarded.",
            )

        try:
            claim.status = BoardCandidateClaim.Status.DISCARDED
            claim.save()
        except IntegrityError:
            logger.warning(
                "Error discarding Board Candidate Claim for candidate %s, key %s",
                claim.candidate.member.login,
                claim.key,
            )
            return ClaimResult(
                ok=False,
                code="ERROR",
                message=GENERIC_ERROR_MSG,
            )
        except ValidationError as e:
            messages = []
            for msgs in e.message_dict.values():
                messages.extend(msgs)
            return ClaimResult(
                ok=False,
                code="VALIDATION_ERROR",
                message=" ".join(messages),
            )

        return ClaimResult(
            ok=True,
            code="SUCCESS",
            message="Claim discarded successfully.",
            claim=claim,
        )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    @validate_pydantic_input(ClaimResult)
    def submit_board_candidate_claim(
        self, info: Info, input_data: SubmitClaimInput
    ) -> ClaimResult:
        """Submit a claim."""
        validated = input_data.validated_data  # type: ignore[attr-defined]
        user = info.context.request.user
        if user.github_user is None:
            return ClaimResult(ok=False, code="FORBIDDEN", message=ACCESS_DENIED_MSG)

        try:
            claim = BoardCandidateClaim.objects.select_for_update().get(
                board__year=validated.year,
                candidate__member__login=user.github_user.login,
                key=validated.key,
            )
        except BoardCandidateClaim.DoesNotExist:
            return ClaimResult(ok=False, code="NOT_FOUND", message=CLAIM_NOT_FOUND_MSG)

        if claim.status != BoardCandidateClaim.Status.DRAFT:
            return ClaimResult(
                ok=False,
                code="INVALID_STATUS",
                message="Only draft claims can be submitted.",
            )

        if not claim.evidences.filter(is_removed=False).exists():
            return ClaimResult(
                ok=False,
                code="VALIDATION_ERROR",
                message="Claim must have at least one evidence to submit.",
            )

        result = None
        try:
            claim.status = BoardCandidateClaim.Status.SUBMITTED
            claim.save()
        except IntegrityError:
            logger.warning(
                "Error submitting Board Candidate Claim for candidate %s, key %s",
                claim.candidate.member.login,
                claim.key,
            )
            result = ClaimResult(
                ok=False,
                code="ERROR",
                message=GENERIC_ERROR_MSG,
            )
        except ValidationError as e:
            messages = []
            for msgs in e.message_dict.values():
                messages.extend(msgs)
            return ClaimResult(
                ok=False,
                code="VALIDATION_ERROR",
                message=" ".join(messages),
            )
        else:
            result = ClaimResult(
                ok=True,
                code="SUCCESS",
                message="Claim submitted successfully.",
                claim=claim,
            )

        return result

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    @validate_pydantic_input(ClaimResult)
    def withdraw_board_candidate_claim(
        self, info: Info, input_data: WithdrawClaimInput
    ) -> ClaimResult:
        """Withdraw a claim."""
        validated = input_data.validated_data  # type: ignore[attr-defined]
        user = info.context.request.user
        if user.github_user is None:
            return ClaimResult(ok=False, code="FORBIDDEN", message=ACCESS_DENIED_MSG)

        try:
            claim = BoardCandidateClaim.objects.select_for_update().get(
                board__year=validated.year,
                candidate__member__login=user.github_user.login,
                key=validated.key,
            )
        except BoardCandidateClaim.DoesNotExist:
            return ClaimResult(ok=False, code="NOT_FOUND", message=CLAIM_NOT_FOUND_MSG)

        if claim.status not in {
            BoardCandidateClaim.Status.SUBMITTED,
            BoardCandidateClaim.Status.APPROVED,
        }:
            return ClaimResult(
                ok=False,
                code="INVALID_STATUS",
                message="Only submitted or approved claims can be withdrawn.",
            )

        try:
            claim.status = BoardCandidateClaim.Status.WITHDRAWN
            claim.withdrawn_reason = validated.withdrawn_reason
            claim.withdrawn_at = timezone.now()
            claim.save()
        except IntegrityError:
            logger.warning(
                "Error withdrawing Board Candidate Claim for candidate %s, key %s",
                claim.candidate.member.login,
                claim.key,
            )
            return ClaimResult(
                ok=False,
                code="ERROR",
                message=GENERIC_ERROR_MSG,
            )
        except ValidationError as e:
            messages = []
            for msgs in e.message_dict.values():
                messages.extend(msgs)
            return ClaimResult(
                ok=False,
                code="VALIDATION_ERROR",
                message=" ".join(messages),
            )

        return ClaimResult(
            ok=True,
            code="SUCCESS",
            message="Claim withdrawn successfully.",
            claim=claim,
        )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    @validate_pydantic_input(ReorderClaimsResult)
    def reorder_board_candidate_claims(
        self, info: Info, input_data: ReorderClaimsInput
    ) -> ReorderClaimsResult:
        """Reorder claims for a candidate in a board year."""
        validated = input_data.validated_data  # type: ignore[attr-defined]
        user = info.context.request.user
        if user.github_user is None:
            return ReorderClaimsResult(ok=False, code="FORBIDDEN", message=ACCESS_DENIED_MSG)

        login = user.github_user.login
        keys = validated.keys

        claims = list(
            BoardCandidateClaim.objects.filter(
                board__year=validated.year,
                candidate__member__login=login,
                key__in=keys,
            )
            .select_for_update(of=("self",))
            .select_related("candidate__member")
        )

        if len(claims) != len(keys):
            return ReorderClaimsResult(
                ok=False,
                code="NOT_FOUND",
                message="One or more claims were not found.",
            )

        keys_to_order = {key: idx for idx, key in enumerate(keys)}
        for claim in claims:
            claim.order = keys_to_order[claim.key]

        if any(claim.status != BoardCandidateClaim.Status.APPROVED for claim in claims):
            return ReorderClaimsResult(
                ok=False,
                code="VALIDATION_ERROR",
                message="Only approved claims can be reordered.",
            )

        BoardCandidateClaim.objects.bulk_update(claims, ["order"])

        ordered_claims = (
            BoardCandidateClaim.objects.filter(
                board__year=validated.year,
                candidate__member__login=login,
                key__in=keys,
            )
            .select_related("candidate__member", "board")
            .order_by("order", "nest_created_at")
        )

        return ReorderClaimsResult(
            ok=True,
            code="SUCCESS",
            message="Claims reordered successfully.",
            claims=list(ordered_claims),
        )
