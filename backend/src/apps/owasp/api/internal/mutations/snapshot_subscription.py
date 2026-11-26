"""OWASP snapshot subscription GraphQL mutations."""

import enum
import functools
import logging

import pydantic
import strawberry
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from strawberry.types import Info

from apps.nest.api.internal.permissions import IsAuthenticated
from apps.owasp.api.internal.nodes.snapshot_subscription import SnapshotSubscriptionNode
from apps.owasp.models.snapshot_subscription import MAX_NAME_LENGTH, SnapshotSubscription

logger = logging.getLogger(__name__)


@strawberry.enum
class SnapshotFrequency(enum.Enum):
    """Snapshot subscription frequency."""

    WEEKLY = "weekly"
    MONTHLY = "monthly"


@strawberry.type
class FieldError:
    """Structured field-level validation error."""

    field: str
    messages: list[str]


class CreateSubscriptionPydanticInput(pydantic.BaseModel):
    """Pydantic validation for creating a snapshot subscription."""

    name: str = pydantic.Field(default="", max_length=MAX_NAME_LENGTH)
    frequency: str = pydantic.Field(default="weekly")
    include_chapters: bool = False
    include_events: bool = False
    include_issues: bool = False
    include_posts: bool = False
    include_projects: bool = False
    include_pull_requests: bool = False
    include_releases: bool = False
    include_users: bool = False
    project_ids: list[int] | None = None
    chapter_ids: list[int] | None = None
    committee_ids: list[int] | None = None

    @pydantic.field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        """Strip whitespace from name."""
        return v.strip()

    @pydantic.field_validator("frequency")
    @classmethod
    def validate_frequency(cls, v: str) -> str:
        """Validate frequency is weekly or monthly."""
        v = v.lower()
        if v not in ("weekly", "monthly"):
            message = "Frequency must be 'weekly' or 'monthly'."
            raise ValueError(message)
        return v


class UpdateSubscriptionPydanticInput(pydantic.BaseModel):
    """Pydantic validation for updating a snapshot subscription."""

    name: str | None = pydantic.Field(default=None, max_length=MAX_NAME_LENGTH)
    frequency: str | None = None
    include_chapters: bool | None = None
    include_events: bool | None = None
    include_issues: bool | None = None
    include_posts: bool | None = None
    include_projects: bool | None = None
    include_pull_requests: bool | None = None
    include_releases: bool | None = None
    include_users: bool | None = None
    project_ids: list[int] | None = None
    chapter_ids: list[int] | None = None
    committee_ids: list[int] | None = None

    @pydantic.field_validator("name")
    @classmethod
    def strip_name(cls, v: str | None) -> str | None:
        """Strip whitespace from name if provided."""
        if v is not None:
            return v.strip()
        return v

    @pydantic.field_validator("frequency")
    @classmethod
    def validate_frequency(cls, v: str | None) -> str | None:
        """Validate frequency is weekly or monthly."""
        if v is not None:
            v = v.lower()
            if v not in ("weekly", "monthly"):
                message = "Frequency must be 'weekly' or 'monthly'."
                raise ValueError(message)
        return v


class UnsubscribeTokenPydanticInput(pydantic.BaseModel):
    """Pydantic validation for unsubscribe by token."""

    token: str = pydantic.Field(min_length=1)

    @pydantic.field_validator("token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Reject blank tokens."""
        if not v.strip():
            message = "Invalid unsubscribe token."
            raise ValueError(message)
        return v.strip()


@strawberry.experimental.pydantic.input(model=CreateSubscriptionPydanticInput, all_fields=True)
class CreateSnapshotSubscriptionInput:
    """Input for creating a snapshot subscription."""


@strawberry.experimental.pydantic.input(model=UpdateSubscriptionPydanticInput, all_fields=True)
class UpdateSnapshotSubscriptionInput:
    """Input for updating a snapshot subscription."""


@strawberry.experimental.pydantic.input(model=UnsubscribeTokenPydanticInput, all_fields=True)
class UnsubscribeTokenInput:
    """Input for unsubscribing by token."""


@strawberry.type
class SnapshotSubscriptionResult:
    """Result payload for snapshot subscription mutations."""

    ok: bool
    code: str | None = None
    message: str | None = None
    subscription: SnapshotSubscriptionNode | None = None
    field_errors: list[FieldError] | None = None


def validate_pydantic_input(result_type):
    """Validate pydantic input and return field errors on failure."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            input_data = kwargs.get("input_data") or next(
                (a for a in args if hasattr(a, "to_pydantic")), None
            )
            if input_data is not None and hasattr(input_data, "to_pydantic"):
                try:
                    validated = input_data.to_pydantic()
                    input_data.validated_data = validated
                except pydantic.ValidationError as exc:
                    field_errors = []
                    for error in exc.errors():
                        field_name = ".".join(str(loc) for loc in error["loc"])
                        field_errors.append(FieldError(field=field_name, messages=[error["msg"]]))
                    return result_type(
                        ok=False,
                        code="VALIDATION_ERROR",
                        message=field_errors[0].messages[0]
                        if field_errors
                        else "Validation failed.",
                        field_errors=field_errors,
                    )
            return func(*args, **kwargs)

        return wrapper

    return decorator


@strawberry.type
class SnapshotSubscriptionMutations:
    """GraphQL mutations for snapshot subscription management."""

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @validate_pydantic_input(SnapshotSubscriptionResult)
    def create_snapshot_subscription(
        self,
        info: Info,
        input_data: CreateSnapshotSubscriptionInput,
    ) -> SnapshotSubscriptionResult:
        """Create a new snapshot subscription for the logged-in user."""
        validated = input_data.validated_data  # type: ignore[attr-defined]
        user = info.context.request.user

        kwargs = {
            "include_chapters": validated.include_chapters,
            "include_events": validated.include_events,
            "include_issues": validated.include_issues,
            "include_posts": validated.include_posts,
            "include_projects": validated.include_projects,
            "include_pull_requests": validated.include_pull_requests,
            "include_releases": validated.include_releases,
            "include_users": validated.include_users,
        }

        try:
            with transaction.atomic():
                subscription = SnapshotSubscription.create(
                    user=user,
                    frequency=validated.frequency,
                    name=validated.name,
                    **kwargs,
                )

                subscription.set_m2m_fields(
                    project_ids=validated.project_ids,
                    chapter_ids=validated.chapter_ids,
                    committee_ids=validated.committee_ids,
                )

                subscription.clean()

                subscription.validate_unique_setup()

        except ValidationError as e:
            return SnapshotSubscriptionResult(
                ok=False,
                code="VALIDATION_ERROR",
                message=e.message,
            )

        return SnapshotSubscriptionResult(
            ok=True,
            code="SUCCESS",
            message="Subscription created successfully.",
            subscription=subscription,
        )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @validate_pydantic_input(SnapshotSubscriptionResult)
    def update_snapshot_subscription(
        self,
        info: Info,
        subscription_id: int,
        input_data: UpdateSnapshotSubscriptionInput,
    ) -> SnapshotSubscriptionResult:
        """Update a specific snapshot subscription."""
        validated = input_data.validated_data  # type: ignore[attr-defined]
        user = info.context.request.user

        try:
            subscription = SnapshotSubscription.objects.get(
                id=subscription_id,
                user=user,
            )
        except SnapshotSubscription.DoesNotExist:
            return SnapshotSubscriptionResult(
                ok=False,
                code="NOT_FOUND",
                message="Subscription not found.",
            )

        update_kwargs = {}
        for field in (
            "include_chapters",
            "include_events",
            "include_issues",
            "include_posts",
            "include_projects",
            "include_pull_requests",
            "include_releases",
            "include_users",
        ):
            value = getattr(validated, field)
            if value is not None:
                update_kwargs[field] = value

        try:
            with transaction.atomic():
                subscription.update(
                    frequency=validated.frequency,
                    name=validated.name,
                    **update_kwargs,
                )

                subscription.set_m2m_fields(
                    project_ids=validated.project_ids,
                    chapter_ids=validated.chapter_ids,
                    committee_ids=validated.committee_ids,
                )

                subscription.clean()

                subscription.validate_unique_setup()

        except IntegrityError:
            return SnapshotSubscriptionResult(
                ok=False,
                code="ERROR",
                message="A subscription with this name already exists.",
            )
        except ValidationError as e:
            return SnapshotSubscriptionResult(
                ok=False,
                code="VALIDATION_ERROR",
                message=e.message,
            )

        return SnapshotSubscriptionResult(
            ok=True,
            code="SUCCESS",
            message="Subscription updated successfully.",
            subscription=subscription,
        )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def delete_snapshot_subscription(
        self,
        info: Info,
        subscription_id: int,
    ) -> SnapshotSubscriptionResult:
        """Permanently delete a specific snapshot subscription."""
        user = info.context.request.user

        try:
            subscription = SnapshotSubscription.objects.get(
                id=subscription_id,
                user=user,
            )
        except SnapshotSubscription.DoesNotExist:
            return SnapshotSubscriptionResult(
                ok=False,
                code="NOT_FOUND",
                message="Subscription not found.",
            )

        subscription.delete()

        return SnapshotSubscriptionResult(
            ok=True,
            code="SUCCESS",
            message="Subscription deleted successfully.",
        )

    @strawberry.mutation
    @validate_pydantic_input(SnapshotSubscriptionResult)
    def unsubscribe_by_token(
        self, input_data: UnsubscribeTokenInput
    ) -> SnapshotSubscriptionResult:
        """Unsubscribe using a token from an email link. No auth required."""
        validated = input_data.validated_data  # type: ignore[attr-defined]

        try:
            subscription = SnapshotSubscription.objects.get(
                unsubscribe_token=validated.token,
            )
        except (SnapshotSubscription.DoesNotExist, ValidationError):
            return SnapshotSubscriptionResult(
                ok=False,
                code="NOT_FOUND",
                message="Invalid unsubscribe token.",
            )

        subscription.delete()

        return SnapshotSubscriptionResult(
            ok=True,
            code="SUCCESS",
            message="Successfully unsubscribed.",
        )
