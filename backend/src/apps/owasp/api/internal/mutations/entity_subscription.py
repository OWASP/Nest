"""OWASP entity subscription GraphQL mutations."""

import strawberry
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from strawberry.types import Info

from apps.nest.api.internal.permissions import IsAuthenticated
from apps.nest.models import User
from apps.owasp.api.internal.nodes.entity_subscription import EntitySubscriptionNode
from apps.owasp.models.entity_subscription import MAX_ENTITY_SUBSCRIPTIONS, EntitySubscription

ENTITY_TYPES = frozenset(("chapter", "committee", "project"))
VALID_FREQUENCIES = frozenset(dict(EntitySubscription.Frequency.choices))
MAX_NAME_LENGTH = 100


MAX_ENTITY_PREFERENCES_PER_SUBSCRIPTION = 50


@strawberry.input
class EntityPreferenceInput:
    """Input for per-entity content preferences."""

    entity_id: int
    entity_type: str
    include_issues: bool = True
    include_pull_requests: bool = True
    include_releases: bool = True


@strawberry.input
class CreateEntitySubscriptionInput:
    """Input for creating an entity subscription."""

    entity_preferences: list[EntityPreferenceInput]
    frequency: str = "weekly"
    name: str = ""


@strawberry.input
class UpdateEntitySubscriptionInput:
    """Input for updating an entity subscription."""

    entity_preferences: list[EntityPreferenceInput] | None = None
    frequency: str | None = None
    name: str | None = None


@strawberry.type
class EntitySubscriptionResult:
    """Result payload for entity subscription mutations."""

    ok: bool
    message: str
    subscription: EntitySubscriptionNode | None = None


def _validate_frequency(frequency):
    """Validate frequency value. Returns error message or None."""
    if frequency is not None and frequency not in VALID_FREQUENCIES:
        return f"Frequency must be one of: {', '.join(sorted(VALID_FREQUENCIES))}."
    return None


def _validate_entity_preferences(preferences):
    """Validate entity preferences. Returns error message or None."""
    if not preferences:
        return "Entity subscriptions must have at least one entity preference."

    if len(preferences) > MAX_ENTITY_PREFERENCES_PER_SUBSCRIPTION:
        return (
            f"Entity subscriptions can have at most "
            f"{MAX_ENTITY_PREFERENCES_PER_SUBSCRIPTION} preferences."
        )

    seen = set()
    for pref in preferences:
        if pref.entity_type not in ENTITY_TYPES:
            return f"Entity type must be one of: {', '.join(sorted(ENTITY_TYPES))}."
        if pref.entity_id <= 0:
            return "Entity ID must be a positive integer."
        key = (pref.entity_type, pref.entity_id)
        if key in seen:
            return f"Duplicate entity: {pref.entity_type} with ID {pref.entity_id}."
        seen.add(key)

    return None


def _validate_name(name):
    """Validate name field. Returns error message or None."""
    if name is not None and len(name.strip()) > MAX_NAME_LENGTH:
        return f"Name must be {MAX_NAME_LENGTH} characters or fewer."
    return None


@strawberry.type
class EntitySubscriptionMutations:
    """GraphQL mutations for entity subscription management."""

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def create_entity_subscription(
        self,
        info: Info,
        input_data: CreateEntitySubscriptionInput,
    ) -> EntitySubscriptionResult:
        """Create a new entity subscription for the logged-in user."""
        user = info.context.request.user

        error = _validate_frequency(input_data.frequency)
        if error:
            return EntitySubscriptionResult(ok=False, message=error)

        error = _validate_name(input_data.name)
        if error:
            return EntitySubscriptionResult(ok=False, message=error)

        error = _validate_entity_preferences(input_data.entity_preferences)
        if error:
            return EntitySubscriptionResult(ok=False, message=error)

        try:
            with transaction.atomic():
                subscription = EntitySubscription.create(
                    user=user,
                    frequency=input_data.frequency,
                    name=input_data.name.strip(),
                )

                if subscription is None:
                    return EntitySubscriptionResult(
                        ok=False,
                        message="Maximum number of entity subscriptions reached.",
                    )

                subscription.sync_preferences(
                    [
                        {
                            "entity_type": p.entity_type,
                            "entity_id": p.entity_id,
                            "include_issues": p.include_issues,
                            "include_pull_requests": p.include_pull_requests,
                            "include_releases": p.include_releases,
                        }
                        for p in input_data.entity_preferences
                    ]
                )
        except (IntegrityError, ValidationError) as exc:
            msg = (
                str(exc)
                if isinstance(exc, ValidationError)
                else "Failed to create subscription preferences."
            )
            return EntitySubscriptionResult(
                ok=False,
                message=msg,
            )

        return EntitySubscriptionResult(
            ok=True,
            message="Subscription created successfully.",
            subscription=subscription,
        )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def update_entity_subscription(
        self,
        info: Info,
        subscription_id: int,
        input_data: UpdateEntitySubscriptionInput,
    ) -> EntitySubscriptionResult:
        """Update a specific entity subscription."""
        user = info.context.request.user

        try:
            subscription = EntitySubscription.objects.get(
                id=subscription_id,
                user=user,
            )
        except EntitySubscription.DoesNotExist:
            return EntitySubscriptionResult(
                ok=False,
                message="Subscription not found.",
            )

        error = _validate_frequency(input_data.frequency)
        if error:
            return EntitySubscriptionResult(ok=False, message=error)

        error = _validate_name(input_data.name)
        if error:
            return EntitySubscriptionResult(ok=False, message=error)

        if input_data.entity_preferences is not None:
            error = _validate_entity_preferences(input_data.entity_preferences)
            if error:
                return EntitySubscriptionResult(ok=False, message=error)

        update_kwargs = {}
        if input_data.name is not None:
            update_kwargs["name"] = input_data.name.strip()

        try:
            with transaction.atomic():
                subscription.update(frequency=input_data.frequency, **update_kwargs)

                if input_data.entity_preferences is not None:
                    subscription.sync_preferences(
                        [
                            {
                                "entity_type": p.entity_type,
                                "entity_id": p.entity_id,
                                "include_issues": p.include_issues,
                                "include_pull_requests": p.include_pull_requests,
                                "include_releases": p.include_releases,
                            }
                            for p in input_data.entity_preferences
                        ]
                    )
        except (IntegrityError, ValidationError) as exc:
            msg = (
                str(exc)
                if isinstance(exc, ValidationError)
                else "Failed to update subscription preferences."
            )
            return EntitySubscriptionResult(
                ok=False,
                message=msg,
            )

        return EntitySubscriptionResult(
            ok=True,
            message="Subscription updated successfully.",
            subscription=subscription,
        )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def cancel_entity_subscription(
        self,
        info: Info,
        subscription_id: int,
    ) -> EntitySubscriptionResult:
        """Deactivate a specific entity subscription."""
        user = info.context.request.user

        try:
            subscription = EntitySubscription.objects.get(
                id=subscription_id,
                user=user,
            )
        except EntitySubscription.DoesNotExist:
            return EntitySubscriptionResult(
                ok=False,
                message="Subscription not found.",
            )

        subscription.is_active = False
        subscription.save()

        return EntitySubscriptionResult(
            ok=True,
            message="Subscription cancelled successfully.",
            subscription=subscription,
        )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def delete_entity_subscription(
        self,
        info: Info,
        subscription_id: int,
    ) -> EntitySubscriptionResult:
        """Permanently delete a specific entity subscription."""
        user = info.context.request.user

        try:
            subscription = EntitySubscription.objects.get(
                id=subscription_id,
                user=user,
            )
        except EntitySubscription.DoesNotExist:
            return EntitySubscriptionResult(
                ok=False,
                message="Subscription not found.",
            )

        subscription.delete()

        return EntitySubscriptionResult(
            ok=True,
            message="Subscription deleted successfully.",
        )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def reactivate_entity_subscription(
        self,
        info: Info,
        subscription_id: int,
    ) -> EntitySubscriptionResult:
        """Reactivate an inactive entity subscription."""
        user = info.context.request.user

        try:
            subscription = EntitySubscription.objects.get(
                id=subscription_id,
                user=user,
            )
        except EntitySubscription.DoesNotExist:
            return EntitySubscriptionResult(
                ok=False,
                message="Subscription not found.",
            )

        if subscription.is_active:
            return EntitySubscriptionResult(
                ok=False,
                message="Subscription is already active.",
            )

        with transaction.atomic():
            if getattr(user, "pk", None):
                User.objects.select_for_update().filter(pk=user.pk).exists()

            active_count = EntitySubscription.objects.filter(
                user=user,
                is_active=True,
            ).count()
            if active_count >= MAX_ENTITY_SUBSCRIPTIONS:
                return EntitySubscriptionResult(
                    ok=False,
                    message="Maximum number of active entity subscriptions reached.",
                )

            subscription.is_active = True
            subscription.save()

        return EntitySubscriptionResult(
            ok=True,
            message="Subscription reactivated successfully.",
            subscription=subscription,
        )

    @strawberry.mutation
    def unsubscribe_entity_by_token(self, token: str) -> EntitySubscriptionResult:
        """Unsubscribe using a token from an email link. No auth required."""
        try:
            subscription = EntitySubscription.objects.get(unsubscribe_token=token)
        except (EntitySubscription.DoesNotExist, ValidationError):
            return EntitySubscriptionResult(
                ok=False,
                message="Invalid unsubscribe token.",
            )

        if not subscription.is_active:
            return EntitySubscriptionResult(
                ok=False,
                message="Subscription is already inactive.",
            )

        subscription.is_active = False
        subscription.save()

        return EntitySubscriptionResult(
            ok=True,
            message="Successfully unsubscribed.",
            subscription=subscription,
        )
