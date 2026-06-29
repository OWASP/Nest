"""OWASP snapshot subscription GraphQL mutations."""

import strawberry
from strawberry.types import Info

from apps.nest.api.internal.permissions import IsAuthenticated
from apps.owasp.api.internal.nodes.snapshot_subscription import SnapshotSubscriptionNode
from apps.owasp.models.snapshot_subscription import SnapshotSubscription


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

        if SnapshotSubscription.objects.filter(user=user).exists():
            return SnapshotSubscriptionResult(
                ok=False,
                message="Subscription already exists.",
            )

        if input_data.frequency not in dict(SnapshotSubscription.Frequency.choices):
            return SnapshotSubscriptionResult(
                ok=False,
                message="Invalid frequency. Must be 'weekly' or 'monthly'.",
            )

        subscription = SnapshotSubscription.objects.create(
            user=user,
            frequency=input_data.frequency,
            include_chapters=input_data.include_chapters,
            include_events=input_data.include_events,
            include_issues=input_data.include_issues,
            include_posts=input_data.include_posts,
            include_projects=input_data.include_projects,
            include_pull_requests=input_data.include_pull_requests,
            include_releases=input_data.include_releases,
            include_users=input_data.include_users,
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
        """Update the logged-in user's snapshot subscription."""
        user = info.context.request.user

        try:
            subscription = SnapshotSubscription.objects.get(user=user)
        except SnapshotSubscription.DoesNotExist:
            return SnapshotSubscriptionResult(
                ok=False,
                message="Subscription not found.",
            )

        if input_data.frequency is not None:
            if input_data.frequency not in dict(SnapshotSubscription.Frequency.choices):
                return SnapshotSubscriptionResult(
                    ok=False,
                    message="Invalid frequency. Must be 'weekly' or 'monthly'.",
                )
            subscription.frequency = input_data.frequency

        fields = {
            "include_chapters": input_data.include_chapters,
            "include_events": input_data.include_events,
            "include_issues": input_data.include_issues,
            "include_posts": input_data.include_posts,
            "include_projects": input_data.include_projects,
            "include_pull_requests": input_data.include_pull_requests,
            "include_releases": input_data.include_releases,
            "include_users": input_data.include_users,
        }

        for field_name, value in fields.items():
            if value is not None:
                setattr(subscription, field_name, value)

        subscription.save()

        return SnapshotSubscriptionResult(
            ok=True,
            message="Subscription updated successfully.",
            subscription=subscription,
        )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def cancel_snapshot_subscription(self, info: Info) -> SnapshotSubscriptionResult:
        """Cancel the logged-in user's snapshot subscription."""
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
        except (SnapshotSubscription.DoesNotExist, ValueError):
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
