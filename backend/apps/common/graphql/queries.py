"""Common GraphQL queries."""

from __future__ import annotations

import graphene

from apps.github.models.user import User
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.project import Project


class EntityKeysType(graphene.ObjectType):
    """Type for returning keys of different entities."""

    projects = graphene.List(graphene.String)
    chapters = graphene.List(graphene.String)
    committees = graphene.List(graphene.String)
    users = graphene.List(graphene.String)


class BaseQuery(graphene.ObjectType):
    """Base query."""

    get_all_entity_keys = graphene.Field(EntityKeysType)

    def resolve_get_all_entity_keys(self, info):
        """Resolve all keys for all entity types."""
        project_keys = [
            key.replace("www-project-", "")
            for key in list(Project.objects.values_list("key", flat=True))
            if key
        ]

        chapter_keys = [
            key.replace("www-chapter-", "")
            for key in list(Chapter.objects.values_list("key", flat=True))
            if key
        ]

        committee_keys = [
            key.replace("www-committee-", "")
            for key in list(Committee.objects.values_list("key", flat=True))
            if key
        ]

        user_keys = [key for key in list(User.objects.values_list("login", flat=True)) if key]

        return EntityKeysType(
            projects=project_keys,
            chapters=chapter_keys,
            committees=committee_keys,
            users=user_keys,
        )
