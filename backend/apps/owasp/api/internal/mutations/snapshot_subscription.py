"""OWASP snapshot subscription GraphQL mutations."""

import strawberry
from django.core.exceptions import ValidationError
from strawberry.types import Info

from apps.nest.api.internal.permissions import IsAuthenticated
from apps.owasp.api.internal.nodes.snapshot_subscription import SnapshotSubscriptionNode
from apps.owasp.models.snapshot_subscription import SnapshotSubscription

VALID_FREQUENCIES = frozenset(dict(SnapshotSubscription.Frequency.choices))


@strawberry.input
class CreateSnapshotSubscriptionInput:
    """Input for creating a snapshot subscription."""

    frequency: str = "weekly"
    include_chapters: bool = True
    include_events: bool = True
    include_issues: bool = True
    include_posts: bool = True
    include_projects: bool = True
    include_pull_requests: bool = True
    include_releases: bool = True
    include_users: bool = True


@strawberry.input
class UpdateSnapshotSubscriptionInput:
    """Input for updating a snapshot subscription."""

    frequency: str | None = None
    include_chapters: bool | None = None
    include_events: bool | None = None
    include_issues: bool | None = None
    include_posts: bool | None = None
    include_projects: bool | None = None
    include_pull_requests: bool | None = None
    include_releases: bool | None = None
    include_users: bool | None = None


@strawberry.type
class SnapshotSubscriptionResult:
    """Result payload for snapshot subscription mutations."""

    ok: bool
    message: str
    subscription: SnapshotSubscriptionNode | None = None


def _validate_frequency(frequency):
    """Validate frequency value. Returns error message or None."""
    if frequency is not None and frequency not in VALID_FREQUENCIES:
        return f"Frequency must be one of: {', '.join(sorted(VALID_FREQUENCIES))}."
    return None


@strawberry.type
class SnapshotSubscriptionMutations:
    """GraphQL mutations for snapshot subscription management."""

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def create_snapshot_subscription(
        self,
        info: Info,
        input_data: CreateSnapshotSubscriptionInput,
    ) -> SnapshotSubscriptionResult:
        """Create a new snapshot subscription for the logged-in user."""
        user = info.context.request.user

        error = _validate_frequency(input_data.frequency)
        if error:
            return SnapshotSubscriptionResult(ok=False, message=error)

        kwargs = {
            "include_chapters": input_data.include_chapters,
            "include_events": input_data.include_events,
            "include_issues": input_data.include_issues,
            "include_posts": input_data.include_posts,
            "include_projects": input_data.include_projects,
            "include_pull_requests": input_data.include_pull_requests,
            "include_releases": input_data.include_releases,
            "include_users": input_data.include_users,
        }

        subscription = SnapshotSubscription.create(
            user=user,
            frequency=input_data.frequency,
            **kwargs,
        )

        if subscription is None:
            return SnapshotSubscriptionResult(
                ok=False,
                message="Snapshot subscription with this User already exists.",
            )

        return SnapshotSubscriptionResult(
            ok=True,
            message="Subscription created successfully.",
            subscription=subscription,
        )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def update_snapshot_subscription(
        self,
        info: Info,
        input_data: UpdateSnapshotSubscriptionInput,
    ) -> SnapshotSubscriptionResult:
        """Update the user's snapshot subscription."""
        user = info.context.request.user

        try:
            subscription = SnapshotSubscription.objects.get(user=user)
        except SnapshotSubscription.DoesNotExist:
            return SnapshotSubscriptionResult(
                ok=False,
                message="Subscription not found.",
            )

        error = _validate_frequency(input_data.frequency)
        if error:
            return SnapshotSubscriptionResult(ok=False, message=error)

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
            value = getattr(input_data, field)
            if value is not None:
                update_kwargs[field] = value

        subscription.update(frequency=input_data.frequency, **update_kwargs)

        return SnapshotSubscriptionResult(
            ok=True,
            message="Subscription updated successfully.",
            subscription=subscription,
        )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def cancel_snapshot_subscription(
        self,
        info: Info,
    ) -> SnapshotSubscriptionResult:
        """Cancel the user's snapshot subscription."""
        user = info.context.request.user

        try:
            subscription = SnapshotSubscription.objects.get(user=user)
        except SnapshotSubscription.DoesNotExist:
            return SnapshotSubscriptionResult(
                ok=False,
                message="Subscription not found.",
            )

        subscription.is_active = False
        subscription.save()

        return SnapshotSubscriptionResult(
            ok=True,
            message="Subscription cancelled successfully.",
            subscription=subscription,
        )

    @strawberry.mutation
    def unsubscribe_by_token(self, token: str) -> SnapshotSubscriptionResult:
        """Unsubscribe using a token from an email link. No auth required."""
        try:
            subscription = SnapshotSubscription.objects.get(unsubscribe_token=token)
        except (SnapshotSubscription.DoesNotExist, ValidationError):
            return SnapshotSubscriptionResult(
                ok=False,
                message="Invalid unsubscribe token.",
            )

        if not subscription.is_active:
            return SnapshotSubscriptionResult(
                ok=False,
                message="Subscription is already inactive.",
            )

        subscription.is_active = False
        subscription.save()

        return SnapshotSubscriptionResult(
            ok=True,
            message="Successfully unsubscribed.",
            subscription=subscription,
        )
