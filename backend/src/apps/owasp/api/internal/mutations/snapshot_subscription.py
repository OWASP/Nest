"""OWASP snapshot subscription GraphQL mutations."""

import enum

import strawberry
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from strawberry.types import Info

from apps.nest.api.internal.permissions import IsAuthenticated
from apps.owasp.api.internal.nodes.snapshot_subscription import SnapshotSubscriptionNode
from apps.owasp.models.snapshot_subscription import SnapshotSubscription


@strawberry.enum
class SnapshotFrequency(enum.Enum):
    """Snapshot subscription frequency."""

    WEEKLY = "weekly"
    MONTHLY = "monthly"


@strawberry.input
class CreateSnapshotSubscriptionInput:
    """Input for creating a snapshot subscription."""

    name: str = ""
    frequency: SnapshotFrequency = SnapshotFrequency.WEEKLY
    include_chapters: bool = False
    include_events: bool = False
    include_issues: bool = False
    include_posts: bool = False
    include_projects: bool = False
    include_pull_requests: bool = False
    include_releases: bool = False
    include_users: bool = False
    subscribed_project_ids: list[int] | None = None
    subscribed_chapter_ids: list[int] | None = None
    subscribed_committee_ids: list[int] | None = None


@strawberry.input
class UpdateSnapshotSubscriptionInput:
    """Input for updating a snapshot subscription."""

    name: str | None = None
    frequency: SnapshotFrequency | None = None
    include_chapters: bool | None = None
    include_events: bool | None = None
    include_issues: bool | None = None
    include_posts: bool | None = None
    include_projects: bool | None = None
    include_pull_requests: bool | None = None
    include_releases: bool | None = None
    include_users: bool | None = None
    subscribed_project_ids: list[int] | None = None
    subscribed_chapter_ids: list[int] | None = None
    subscribed_committee_ids: list[int] | None = None


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

        try:
            with transaction.atomic():
                subscription = SnapshotSubscription.create(
                    user=user,
                    frequency=input_data.frequency.value,
                    name=input_data.name,
                    **kwargs,
                )

                subscription.set_m2m_fields(
                    project_ids=input_data.subscribed_project_ids,
                    chapter_ids=input_data.subscribed_chapter_ids,
                    committee_ids=input_data.subscribed_committee_ids,
                )

                subscription.clean()

                subscription.validate_unique_setup()

        except ValidationError as e:
            return SnapshotSubscriptionResult(
                ok=False,
                message=e.message,
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
        subscription_id: int,
        input_data: UpdateSnapshotSubscriptionInput,
    ) -> SnapshotSubscriptionResult:
        """Update a specific snapshot subscription."""
        user = info.context.request.user

        try:
            subscription = SnapshotSubscription.objects.get(
                id=subscription_id,
                user=user,
            )
        except SnapshotSubscription.DoesNotExist:
            return SnapshotSubscriptionResult(
                ok=False,
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
            value = getattr(input_data, field)
            if value is not None:
                update_kwargs[field] = value

        try:
            with transaction.atomic():
                frequency_value = input_data.frequency.value if input_data.frequency else None
                subscription.update(
                    frequency=frequency_value,
                    name=input_data.name,
                    **update_kwargs,
                )

                subscription.set_m2m_fields(
                    project_ids=input_data.subscribed_project_ids,
                    chapter_ids=input_data.subscribed_chapter_ids,
                    committee_ids=input_data.subscribed_committee_ids,
                )

                subscription.clean()

                subscription.validate_unique_setup()

        except IntegrityError:
            return SnapshotSubscriptionResult(
                ok=False,
                message="A subscription with this name already exists.",
            )
        except ValidationError as e:
            return SnapshotSubscriptionResult(
                ok=False,
                message=e.message,
            )

        return SnapshotSubscriptionResult(
            ok=True,
            message="Subscription updated successfully.",
            subscription=subscription,
        )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def cancel_snapshot_subscription(
        self,
        info: Info,
        subscription_id: int,
    ) -> SnapshotSubscriptionResult:
        """Cancel a specific snapshot subscription."""
        user = info.context.request.user

        try:
            subscription = SnapshotSubscription.objects.get(
                id=subscription_id,
                user=user,
            )
        except SnapshotSubscription.DoesNotExist:
            return SnapshotSubscriptionResult(
                ok=False,
                message="Subscription not found.",
            )

        subscription.deactivate()

        return SnapshotSubscriptionResult(
            ok=True,
            message="Subscription cancelled successfully.",
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
                message="Subscription not found.",
            )

        subscription.delete()

        return SnapshotSubscriptionResult(
            ok=True,
            message="Subscription deleted successfully.",
        )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def reactivate_snapshot_subscription(
        self,
        info: Info,
        subscription_id: int,
    ) -> SnapshotSubscriptionResult:
        """Reactivate an inactive snapshot subscription."""
        user = info.context.request.user

        try:
            subscription = SnapshotSubscription.objects.get(
                id=subscription_id,
                user=user,
            )
        except SnapshotSubscription.DoesNotExist:
            return SnapshotSubscriptionResult(
                ok=False,
                message="Subscription not found.",
            )

        try:
            subscription.reactivate()
        except ValidationError as e:
            return SnapshotSubscriptionResult(
                ok=False,
                message=e.message,
            )

        return SnapshotSubscriptionResult(
            ok=True,
            message="Subscription reactivated successfully.",
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

        subscription.deactivate()

        return SnapshotSubscriptionResult(
            ok=True,
            message="Successfully unsubscribed.",
            subscription=subscription,
        )
