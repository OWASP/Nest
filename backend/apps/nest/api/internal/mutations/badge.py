"""GraphQL mutations for assigning badges to users."""

import strawberry
from strawberry.types import Info

from apps.nest.api.internal.nodes.badge import BadgeNode
from apps.nest.api.internal.permissions import IsAuthenticated
from apps.nest.models import Badge


@strawberry.type
class BadgeMutations:
    """Mutations to manage user-badge assignments."""

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def add_badge_to_user(self, info: Info, badge_id: int) -> list[BadgeNode]:
        """Assign a badge to the authenticated user and return their badges.

        Badges are returned sorted by weight then name.
        """
        user = info.context.request.user
        badge = Badge.objects.get(pk=badge_id)
        user.badges.add(badge)
        return user.badges.order_by("weight", "name")

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def remove_badge_from_user(self, info: Info, badge_id: int) -> list[BadgeNode]:
        """Remove a badge from the authenticated user and return their badges."""
        user = info.context.request.user
        badge = Badge.objects.get(pk=badge_id)
        user.badges.remove(badge)
        return user.badges.order_by("weight", "name")
