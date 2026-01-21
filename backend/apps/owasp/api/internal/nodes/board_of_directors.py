"""OWASP Board of Directors GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.api.internal.nodes.entity_member import EntityMemberNode
from apps.owasp.models.board_of_directors import BoardOfDirectors


@strawberry_django.type(
    BoardOfDirectors,
    fields=[
        "created_at",
        "updated_at",
        "year",
    ],
)
class BoardOfDirectorsNode(strawberry.relay.Node):
    """Board of Directors node."""

    @strawberry_django.field
    def candidates(self, root: BoardOfDirectors) -> list[EntityMemberNode]:
        """Resolve board election candidates."""
        return root.get_candidates()  # type: ignore[call-arg]

    @strawberry_django.field
    def members(self, root: BoardOfDirectors) -> list[EntityMemberNode]:
        """Resolve board members."""
        return root.get_members()  # type: ignore[call-arg]

    @strawberry_django.field
    def owasp_url(self, root: BoardOfDirectors) -> str:
        """Resolve OWASP board election URL."""
        return root.owasp_url
