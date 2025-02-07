"""OWASP chapter GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.owasp.graphql.nodes.chapter import ChapterNode
from apps.owasp.models.chapter import Chapter


class ChapterQuery(BaseQuery):
    """Chapter queries."""

    chapter = graphene.Field(ChapterNode, key=graphene.String(required=True))

    def resolve_chapter(root, info, key):
        """Resolve chapter by key."""
        try:
            normalized_key = "www-chapter-" + key
            return Chapter.objects.get(key=normalized_key)
        except Chapter.DoesNotExist:
            return None
