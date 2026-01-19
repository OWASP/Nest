"""OWASP chapter GraphQL queries."""

import strawberry
import strawberry_django

from apps.owasp.api.internal.nodes.chapter import ChapterNode
from apps.owasp.models.chapter import Chapter

MAX_LIMIT = 1000


@strawberry.type
class ChapterQuery:
    """Chapter queries."""

    @strawberry_django.field
    def chapter(self, key: str) -> ChapterNode | None:
        """Resolve chapter."""
        try:
            return Chapter.objects.get(key=f"www-chapter-{key}")
        except Chapter.DoesNotExist:
            return None

    @strawberry_django.field
    def recent_chapters(self, limit: int = 8) -> list[ChapterNode]:
        """Resolve recent chapters."""
        return (
            Chapter.active_chapters.order_by("-created_at")[:limit]
            if (limit := min(limit, MAX_LIMIT)) > 0
            else []
        )
