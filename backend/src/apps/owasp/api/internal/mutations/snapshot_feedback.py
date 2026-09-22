"""OWASP snapshot feedback GraphQL mutations."""

import pydantic
import strawberry
from strawberry.types import Info

from apps.nest.api.internal.permissions import IsAuthenticated
from apps.owasp.api.internal.mutations.snapshot_subscription import (
    FieldError,
    validate_pydantic_input,
)
from apps.owasp.api.internal.nodes.snapshot_feedback import SnapshotFeedbackNode
from apps.owasp.models.snapshot import Snapshot
from apps.owasp.models.snapshot_feedback import MAX_RATING, MIN_RATING, SnapshotFeedback

MAX_COMMENT_LENGTH = 1000


class SubmitFeedbackPydanticInput(pydantic.BaseModel):
    """Pydantic validation for submitting snapshot feedback."""

    snapshot_key: str = pydantic.Field(min_length=1)
    rating: int
    comment: str = ""

    @pydantic.field_validator("comment")
    @classmethod
    def strip_comment(cls, v: str) -> str:
        """Strip whitespace from comment."""
        return v.strip()

    @pydantic.field_validator("comment")
    @classmethod
    def validate_comment_length(cls, v: str) -> str:
        """Validate comment does not exceed max length."""
        if len(v) > MAX_COMMENT_LENGTH:
            message = f"Comment cannot exceed {MAX_COMMENT_LENGTH} characters."
            raise ValueError(message)
        return v

    @pydantic.field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        """Validate rating is within the allowed range."""
        if not isinstance(v, int) or v < MIN_RATING or v > MAX_RATING:
            message = f"Rating must be a whole number between {MIN_RATING} and {MAX_RATING}."
            raise ValueError(message)
        return v


@strawberry.experimental.pydantic.input(model=SubmitFeedbackPydanticInput, all_fields=True)
class SubmitSnapshotFeedbackInput:
    """Input for submitting or updating snapshot feedback."""


@strawberry.type
class SnapshotFeedbackResult:
    """Result payload for snapshot feedback mutations."""

    ok: bool
    code: str | None = None
    message: str
    feedback: SnapshotFeedbackNode | None = None
    field_errors: list[FieldError] | None = None


@strawberry.type
class SnapshotFeedbackMutations:
    """GraphQL mutations for snapshot feedback management."""

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @validate_pydantic_input(SnapshotFeedbackResult)  # type: ignore[attr-defined]
    def submit_snapshot_feedback(
        self,
        info: Info,
        input_data: SubmitSnapshotFeedbackInput,
    ) -> SnapshotFeedbackResult:
        """Create or update the logged-in user's feedback for a snapshot."""
        user = info.context.request.user
        validated = input_data.validated_data  # type: ignore[attr-defined]

        try:
            snapshot = Snapshot.objects.get(
                key=validated.snapshot_key,
                status=Snapshot.Status.COMPLETED,
            )
        except Snapshot.DoesNotExist:
            return SnapshotFeedbackResult(
                ok=False,
                message="Snapshot not found.",
            )

        feedback, created = SnapshotFeedback.submit(
            snapshot=snapshot,
            user=user,
            rating=validated.rating,
            comment=validated.comment,
        )

        return SnapshotFeedbackResult(
            ok=True,
            message="Thanks for your feedback!" if created else "Feedback updated successfully.",
            feedback=feedback,
        )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def delete_snapshot_feedback(
        self,
        info: Info,
        snapshot_key: str,
    ) -> SnapshotFeedbackResult:
        """Delete the logged-in user's feedback for a snapshot."""
        user = info.context.request.user

        try:
            feedback = SnapshotFeedback.objects.get(
                snapshot__key=snapshot_key,
                user=user,
            )
        except SnapshotFeedback.DoesNotExist:
            return SnapshotFeedbackResult(
                ok=False,
                message="Feedback not found.",
            )

        feedback.delete()

        return SnapshotFeedbackResult(
            ok=True,
            message="Feedback removed successfully.",
        )
