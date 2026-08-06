"""OWASP entity subscription GraphQL mutations."""

import strawberry
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from strawberry.types import Info

from apps.nest.api.internal.permissions import IsAuthenticated
from apps.nest.models import User
from apps.owasp.api.internal.nodes.entity_subscription import EntitySubscriptionNode
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.entity_subscription import MAX_ENTITY_SUBSCRIPTIONS, EntitySubscription
from apps.owasp.models.project import Project

ENTITY_MODELS = {
    "chapter": Chapter,
    "committee": Committee,
    "project": Project,
}
VALID_FREQUENCIES = frozenset(dict(EntitySubscription.Frequency.choices))


@strawberry.input
class CreateEntitySubscriptionInput:
    """Input for subscribing to a single entity."""

    entity_id: int
    entity_type: str
    frequency: str = "weekly"


@strawberry.input
class UpdateEntitySubscriptionInput:
    """Input for updating an entity subscription."""

    frequency: str | None = None


@strawberry.type
class EntitySubscriptionResult:
    """Result payload for entity subscription mutations."""

    ok: bool
    message: str
    subscription: EntitySubscriptionNode | None = None


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

        error = None
        if input_data.frequency not in VALID_FREQUENCIES:
            error = f"Frequency must be one of: {', '.join(sorted(VALID_FREQUENCIES))}."
        elif input_data.entity_type not in ENTITY_MODELS:
            error = f"Entity type must be one of: {', '.join(sorted(ENTITY_MODELS))}."
        elif input_data.entity_id <= 0:
            error = "Entity ID must be a positive integer."

        if error:
            return EntitySubscriptionResult(ok=False, message=error)

        entity_model = ENTITY_MODELS[input_data.entity_type]
        if not entity_model.objects.filter(pk=input_data.entity_id).exists():
            return EntitySubscriptionResult(
                ok=False,
                message=f"{input_data.entity_type.capitalize()} not found.",
            )

        try:
            subscription = EntitySubscription.create(
                user=user,
                frequency=input_data.frequency,
                entity_type=input_data.entity_type,
                entity_id=input_data.entity_id,
            )

            if subscription is None:
                return EntitySubscriptionResult(
                    ok=False,
                    message="Maximum number of entity subscriptions reached.",
                )
        except IntegrityError:
            return EntitySubscriptionResult(
                ok=False,
                message="You are already subscribed to this entity.",
            )
        except ValidationError as exc:
            return EntitySubscriptionResult(
                ok=False,
                message=str(exc),
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

        if input_data.frequency is not None and input_data.frequency not in VALID_FREQUENCIES:
            return EntitySubscriptionResult(
                ok=False,
                message=f"Frequency must be one of: {', '.join(sorted(VALID_FREQUENCIES))}.",
            )

        try:
            subscription.update(frequency=input_data.frequency)
        except ValidationError as exc:
            return EntitySubscriptionResult(
                ok=False,
                message=str(exc),
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
