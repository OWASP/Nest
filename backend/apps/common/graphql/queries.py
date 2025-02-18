"""Common GraphQL queries."""

import graphene

from apps.github.models.user import User
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.project import Project


class CountsType(graphene.ObjectType):
    """Counts type."""

    active_projects_count = graphene.Int()
    contributors_count = graphene.Int()
    chapters_count = graphene.Int()
    countries_count = graphene.Int()


class BaseQuery(graphene.ObjectType):
    """Base query."""

    counts_overview = graphene.Field(CountsType)

    def resolve_counts_overview(self, info, **kwargs):
        """Resolve counts overview."""
        active_projects = Project.active_projects_count()
        chapters_count = Chapter.objects.count()
        contributors_count = User.objects.count()
        countries_count = (
            Chapter.objects.filter(country__isnull=False)
            .exclude(country="")
            .values("country")
            .distinct()
            .count()
        )

        return CountsType(
            active_projects_count=active_projects,
            chapters_count=chapters_count,
            contributors_count=contributors_count,
            countries_count=countries_count,
        )
