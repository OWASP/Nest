"""OWASP chapter GraphQL queries."""

import strawberry
import strawberry_django

from apps.common.utils import normalize_limit
from apps.github.models.user import User as GithubUser
from apps.owasp.api.internal.nodes.chapter import ChapterNode
from apps.owasp.models.chapter import Chapter

MIN_SEARCH_QUERY_LENGTH = 3
MAX_SEARCH_QUERY_LENGTH = 100
SEARCH_CHAPTERS_LIMIT = 8
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
    def chapter_countries(self) -> list[str]:
        """Resolve distinct chapter countries."""
        return sorted(
            Chapter.active_chapters.exclude(country="")
            .values_list("country", flat=True)
            .distinct()
        )

    @strawberry_django.field
    def recent_chapters(self, limit: int = 8) -> list[ChapterNode]:
        """Resolve recent chapters."""
        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            return []

        return Chapter.active_chapters.order_by("-created_at")[:normalized_limit]

    @strawberry_django.field
    def search_chapters(self, query: str) -> list[ChapterNode]:
        """Search active chapters by name (case-insensitive, partial match)."""
        cleaned_query = query.strip()
        if (
            len(cleaned_query) < MIN_SEARCH_QUERY_LENGTH
            or len(cleaned_query) > MAX_SEARCH_QUERY_LENGTH
        ):
            return []

        return Chapter.active_chapters.filter(
            name__icontains=cleaned_query,
        ).order_by("name")[:SEARCH_CHAPTERS_LIMIT]

    @strawberry_django.field
    def is_chapter_leader(self, info: strawberry.Info, login: str) -> bool:
        """Check if a GitHub login is an active, reviewed OWASP chapter leader."""
        try:
            github_user = GithubUser.objects.get(login=login)
        except GithubUser.DoesNotExist:
            return False

        return github_user.chapters.exists()
