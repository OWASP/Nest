"""OWASP repository contributor GraphQL queries."""

import graphene
from django.db import models
from django.db.models import F, OuterRef, Subquery, Window
from django.db.models.functions import DenseRank

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.repository_contributor import RepositoryContributorNode
from apps.github.models.repository_contributor import (
    RepositoryContributor as BaseRepositoryContributor,
)
from apps.owasp.models.project import Project


class RepositoryContributorQuery(BaseQuery):
    """Repository contributor queries."""

    top_contributors = graphene.List(
        RepositoryContributorNode, limit=graphene.Int(default_value=15)
    )

    def resolve_top_contributors(root, info, limit):
        """Resolve top contributors only for repositories with projects.

        Args:
        ----
            root: The root query object.
            info: Execution information.
            limit: Maximum number of contributors to return.

        Returns:
        -------
            List of top repository contributors.

        """
        # Perform the complex query with annotations and filtering
        queryset = (
            BaseRepositoryContributor.objects.by_humans()
            .to_community_repositories()
            .filter(repository__project__isnull=False)
            .annotate(
                # Consolidated project details subquery
                project_details=Subquery(
                    Project.repositories.through.objects.filter(
                        repository=OuterRef("repository_id")
                    ).values("project__name", "project__key")[:1]
                ),
                # Composite index-friendly ranking
                rank=Window(
                    expression=DenseRank(),
                    partition_by=[F("user__login"), F("repository")],
                    order_by=F("contributions_count").desc(),
                ),
            )
            .filter(rank=1)  # Keep only the highest contribution per user per repository
            .values(
                "contributions_count",
                "user__avatar_url",
                "user__login",
                "user__name",
                "repository__id",
                project_name=F("project_details__project__name"),
                project_url=F("project_details__project__key"),
            )
            .order_by("-contributions_count")[:limit]
        )

        # Create RepositoryContributorNode instances
        return [
            RepositoryContributorNode(
                avatar_url=contributor["user__avatar_url"],
                contributions_count=contributor["contributions_count"],
                login=contributor["user__login"],
                name=contributor["user__name"],
                project_name=contributor["project_name"],
                project_url=contributor["project_url"],
            )
            for contributor in queryset
        ]


class RepositoryContributor(BaseRepositoryContributor):
    """Extended Repository Contributor model with additional meta options.

    Inherits from the base RepositoryContributor model to avoid redefining the entire model.
    """

    def __str__(self):
        """String representation of the repository contributor.

        Returns:
        -------
            str: A string identifying the contributor.

        """
        return f"{self.user.login} - {self.repository.name}"

    class Meta(BaseRepositoryContributor.Meta):
        """Meta options for RepositoryContributor model."""

        # Extend existing indexes with new composite indexes
        indexes = [
            *BaseRepositoryContributor.Meta.indexes,
            # Composite index for efficient ranking and filtering
            models.Index(
                fields=["user", "repository", "contributions_count"],
                name="user_repo_contributions_composite_idx",
            ),
            # Additional supporting indexes
            models.Index(
                fields=["repository", "contributions_count"], name="repo_contributions_idx"
            ),
            models.Index(fields=["user", "contributions_count"], name="user_contributions_idx"),
        ]
