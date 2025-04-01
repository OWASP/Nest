"""OWASP chapter GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.owasp.graphql.nodes.chapter import ChapterNode
from apps.owasp.models.chapter import Chapter


class ChapterQuery(BaseQuery):
    """Chapter queries."""

    chapter = graphene.Field(ChapterNode, key=graphene.String(required=True))
    recent_chapters = graphene.List(ChapterNode, limit=graphene.Int(default_value=8))

    def resolve_chapter(root, info, key):
        """Resolve chapter by key.

        Args:
            root: The root object.
            info: GraphQL execution info.
            key (str): The key of the chapter.

        Returns:
            Chapter: The chapter object if found, otherwise None.

        """
        try:
            return Chapter.objects.get(key=f"www-chapter-{key}")
        except Chapter.DoesNotExist:
            return None

    def resolve_recent_chapters(root, info, limit):
        """Resolve recent chapters.

        Args:
            root: The root object.
            info: GraphQL execution info.
            limit (int): The maximum number of recent chapters to return.

        Returns:
            QuerySet: A queryset of recent active chapters.

        """
        return Chapter.objects.filter(is_active=True).order_by("-created_at")[:limit]
