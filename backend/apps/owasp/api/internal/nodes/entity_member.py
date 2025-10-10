"""OWASP app entity member node."""

import strawberry
import strawberry_django

from apps.github.api.internal.nodes.user import UserNode
from apps.owasp.models.entity_member import EntityMember


@strawberry_django.type(
    EntityMember,
    fields=[
        "role",
        "member_name",
        "member_email",
        "description",
        "is_active",
        "is_reviewed",
        "order",
    ],
)
class EntityMemberNode(strawberry.relay.Node):
    """Entity member node."""

    member: UserNode | None
