"""OWASP snapshot subscription GraphQL mutations."""

import strawberry
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from strawberry.types import Info

from apps.nest.api.internal.permissions import IsAuthenticated
from apps.owasp.api.internal.nodes.snapshot_subscription import SnapshotSubscriptionNode
from apps.owasp.models.project_subscription_preference import ProjectSubscriptionPreference
from apps.owasp.models.snapshot_subscription import SnapshotSubscription


@strawberry.input
class ProjectPreferenceInput:
    """Input for per-project content preferences."""

    project_id: int
    include_issues: bool = True
    include_pull_requests: bool = True
    include_releases: bool = True


@strawberry.input
class CreateSnapshotSubscriptionInput:
    """Input for creating a snapshot subscription."""

    frequency: str = "weekly"
    include_chapters: bool = True
    include_events: bool = True
    include_posts: bool = True
    include_users: bool = True
    subscribed_chapter_ids: list[int] | None = None
    project_preferences: list[ProjectPreferenceInput] | None = None


@strawberry.input
class UpdateSnapshotSubscriptionInput:
    """Input for updating a snapshot subscription."""

    frequency: str | None = None
    include_chapters: bool | None = None
    include_events: bool | None = None
    include_posts: bool | None = None
    include_users: bool | None = None
    subscribed_chapter_ids: list[int] | None = None
    project_preferences: list[ProjectPreferenceInput] | None = None


@strawberry.type
class SnapshotSubscriptionResult:
    """Result payload for snapshot subscription mutations."""

    ok: bool
    message: str
    subscription: SnapshotSubscriptionNode | None = None


def _sync_project_preferences(
    subscription: SnapshotSubscription,
    preferences: list[ProjectPreferenceInput],
) -> None:
    """Sync per-project preferences for a subscription.

    Replaces all existing project preferences with the provided ones.

    Args:
        subscription: The snapshot subscription instance.
        preferences: List of per-project preference inputs.

    """
    subscription.project_preferences.all().delete()

    for pref in preferences:
        ProjectSubscriptionPreference.objects.create(
            subscription=subscription,
            project_id=pref.project_id,
            include_issues=pref.include_issues,
            include_pull_requests=pref.include_pull_requests,
            include_releases=pref.include_releases,
        )


def _apply_subscription_preferences(
    subscription: SnapshotSubscription,
    input_data: CreateSnapshotSubscriptionInput,
) -> None:
    """Apply preferences from input data to a subscription instance.

    Args:
        subscription: The snapshot subscription instance to update.
        input_data: The input data containing preference values.

    """
    subscription.is_active = True
    subscription.frequency = input_data.frequency
    subscription.include_chapters = input_data.include_chapters
    subscription.include_events = input_data.include_events
    subscription.include_posts = input_data.include_posts
    subscription.include_users = input_data.include_users
    subscription.save()

    if input_data.subscribed_chapter_ids is not None:
        subscription.chapters.set(input_data.subscribed_chapter_ids)

    if input_data.project_preferences is not None:
        _sync_project_preferences(subscription, input_data.project_preferences)


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

        if input_data.frequency not in dict(SnapshotSubscription.Frequency.choices):
            return SnapshotSubscriptionResult(
                ok=False,
                message="Invalid frequency. Must be 'weekly' or 'monthly'.",
            )

        defaults = {
            "frequency": input_data.frequency,
            "include_chapters": input_data.include_chapters,
            "include_events": input_data.include_events,
            "include_posts": input_data.include_posts,
            "include_users": input_data.include_users,
            "is_active": True,
        }

        try:
            with transaction.atomic():
                subscription, created = SnapshotSubscription.objects.get_or_create(
                    user=user,
                    defaults=defaults,
                )
        except IntegrityError:
            return SnapshotSubscriptionResult(
                ok=False,
                message="Subscription already exists.",
            )

        if not created:
            if subscription.is_active:
                return SnapshotSubscriptionResult(
                    ok=False,
                    message="Subscription already exists.",
                )
            _apply_subscription_preferences(subscription, input_data)
            return SnapshotSubscriptionResult(
                ok=True,
                message="Subscription reactivated successfully.",
                subscription=subscription,
            )

        if input_data.subscribed_chapter_ids is not None:
            subscription.chapters.set(input_data.subscribed_chapter_ids)

        if input_data.project_preferences is not None:
            _sync_project_preferences(subscription, input_data.project_preferences)

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
            "include_posts": input_data.include_posts,
            "include_users": input_data.include_users,
        }

        for field_name, value in fields.items():
            if value is not None:
                setattr(subscription, field_name, value)

        subscription.save()

        if input_data.subscribed_chapter_ids is not None:
            subscription.chapters.set(input_data.subscribed_chapter_ids)

        if input_data.project_preferences is not None:
            _sync_project_preferences(subscription, input_data.project_preferences)

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
