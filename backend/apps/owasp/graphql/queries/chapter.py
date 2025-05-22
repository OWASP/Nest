"""OWASP chapter GraphQL queries."""

import strawberry

from apps.owasp.graphql.nodes.chapter import ChapterNode
from apps.owasp.models.chapter import Chapter


@strawberry.type
class ChapterQuery:
    """Chapter queries."""

    @strawberry.field
    def chapter(self, key: str) -> ChapterNode | None:
        """Resolve chapter by key."""
        try:
            return Chapter.objects.get(key=f"www-chapter-{key}")
        except Chapter.DoesNotExist:
            return None

    @strawberry.field
    def recent_chapters(self, limit: int = 8) -> list[ChapterNode]:
        """Resolve recent active chapters."""
        return Chapter.objects.filter(is_active=True).order_by("-created_at")[:limit]
