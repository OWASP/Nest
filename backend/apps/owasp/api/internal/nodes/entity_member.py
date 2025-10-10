"""OWASP app entity member node."""

import strawberry
import strawberry_django

from apps.github.api.internal.nodes.user import UserNode
from apps.owasp.models.entity_member import EntityMember


@strawberry_django.type(
    EntityMember,
    fields=[
        "description",
        "is_active",
        "is_reviewed",
        "member_email",
        "member_name",
        "order",
        "role",
    ],
)
class EntityMemberNode(strawberry.relay.Node):
    """Entity member node."""

    member: UserNode | None
