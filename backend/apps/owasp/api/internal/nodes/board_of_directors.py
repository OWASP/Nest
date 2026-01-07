"""OWASP Board of Directors GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.api.internal.nodes.entity_member import EntityMemberNode
from apps.owasp.models.board_of_directors import BoardOfDirectors


@strawberry_django.type(
    BoardOfDirectors,
    fields=[
        "year",
        "created_at",
        "updated_at",
    ],
)
class BoardOfDirectorsNode(strawberry.relay.Node):
    """Board of Directors node."""

    @strawberry_django.field
    def candidates(self) -> list[EntityMemberNode]:
        """Resolve board election candidates."""
        return self.get_candidates()  # type: ignore[call-arg]

    @strawberry_django.field
    def members(self) -> list[EntityMemberNode]:
        """Resolve board members."""
        return self.get_members()  # type: ignore[call-arg]

    @strawberry_django.field
    def owasp_url(self) -> str:
        """Resolve OWASP board election URL."""
        return self.owasp_url
