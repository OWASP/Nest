"""OWASP Board of Directors GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.api.internal.dataloaders.board_of_directors import (
    CANDIDATES_BY_BOARD_ID_LOADER,
    MEMBERS_BY_BOARD_ID_LOADER,
)
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
    async def candidates(
        self, root: BoardOfDirectors, info: strawberry.Info
    ) -> list[EntityMemberNode]:
        """Resolve board election candidates."""
        return await info.context.owasp_dataloaders[CANDIDATES_BY_BOARD_ID_LOADER].load(root.pk)

    @strawberry_django.field
    async def members(
        self, root: BoardOfDirectors, info: strawberry.Info
    ) -> list[EntityMemberNode]:
        """Resolve board members."""
        return await info.context.owasp_dataloaders[MEMBERS_BY_BOARD_ID_LOADER].load(root.pk)

    @strawberry_django.field(only=["year"])
    def owasp_url(self, root: BoardOfDirectors) -> str:
        """Resolve OWASP board election URL."""
        return root.owasp_url
