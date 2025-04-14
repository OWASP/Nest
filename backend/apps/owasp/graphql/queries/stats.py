"""OWASP stats GraphQL queries."""

import graphene
from django.db.models import Count, FloatField, Value
from django.db.models.expressions import ExpressionWrapper
from django.db.models.functions import Floor

from apps.github.models.user import User
from apps.owasp.graphql.nodes.stats import StatsNode
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.project import Project


class StatsQuery:
    """Stats queries."""

    stats_overview = graphene.Field(StatsNode)

    def resolve_stats_overview(self, info, **kwargs):
        """Resolve stats overview.

        Args:
            self: The StatsQuery instance.
            info: GraphQL execution info.
            **kwargs: Additional arguments.

        Returns:
            StatsNode: A node containing aggregated statistics.

        """
        active_projects_stats = Project.active_projects.aggregate(
            nearest=Floor(
                ExpressionWrapper(Count("id") * 1.0 / Value(10), output_field=FloatField())
            )
            * Value(10)
        )["nearest"]

        active_chapters_stats = Chapter.active_chapters.aggregate(
            nearest=Floor(
                ExpressionWrapper(Count("id") * 1.0 / Value(10), output_field=FloatField())
            )
            * Value(10)
        )["nearest"]

        contributors_stats = User.objects.aggregate(
            nearest=Floor(
                ExpressionWrapper(Count("id") * 1.0 / Value(100), output_field=FloatField())
            )
            * Value(100)
        )["nearest"]

        countries_stats = (
            Chapter.objects.filter(country__isnull=False)
            .exclude(country="")
            .aggregate(
                nearest=Floor(
                    ExpressionWrapper(
                        Count("country", distinct=True) * 1.0 / Value(10),
                        output_field=FloatField(),
                    )
                )
                * Value(10)
            )["nearest"]
        )

        return StatsNode(
            active_projects_stats,
            active_chapters_stats,
            contributors_stats,
            countries_stats,
        )
