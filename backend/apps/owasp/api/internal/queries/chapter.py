"""OWASP chapter GraphQL queries."""

import strawberry

from apps.owasp.api.internal.nodes.chapter import ChapterNode
from apps.owasp.models.chapter import Chapter


@strawberry.type
class ChapterQuery:
    """Chapter queries."""

    @strawberry.field
    def chapter(self, key: str) -> ChapterNode | None:
        """Resolve chapter."""
        try:
            return Chapter.objects.get(key=f"www-chapter-{key}")
        except Chapter.DoesNotExist:
            return None

    @strawberry.field
    def recent_chapters(self, limit: int = 8) -> list[ChapterNode]:
        """Resolve recent chapters."""
        return Chapter.active_chapters.order_by("-created_at")[:limit]
