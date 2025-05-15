"""OWASP repository contributor GraphQL queries."""

from __future__ import annotations

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.repository_contributor import RepositoryContributorNode
from apps.github.models.repository_contributor import RepositoryContributor


class RepositoryContributorQuery(BaseQuery):
    """Repository contributor queries."""

    top_contributors = graphene.List(
        RepositoryContributorNode,
        limit=graphene.Int(default_value=15),
        chapter=graphene.String(required=False),
        committee=graphene.String(required=False),
        organization=graphene.String(required=False),
        project=graphene.String(required=False),
        repository=graphene.String(required=False),
    )

    def resolve_top_contributors(
        root,
        info,
        *,
        limit: int = 15,
        chapter: str | None = None,
        committee: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        repository: str | None = None,
    ) -> list[RepositoryContributorNode]:
        """Resolve top contributors.

        Args:
            root (Any): The root query object.
            info (ResolveInfo): The GraphQL execution context.
            limit (int): Maximum number of contributors to return.
            chapter (str, optional): Chapter key to filter by.
            committee (str, optional): Committee key to filter by.
            organization (str, optional): Organization login to filter by.
            project (str, optional): Project key to filter by.
            repository (str, optional): Repository name to filter by.

        Returns:
            list: List of top contributors with their details.

        """
        top_contributors = RepositoryContributor.get_top_contributors(
            limit=limit,
            chapter=chapter,
            committee=committee,
            organization=organization,
            project=project,
            repository=repository,
        )

        return [
            RepositoryContributorNode(
                avatar_url=tc["avatar_url"],
                contributions_count=tc["contributions_count"],
                login=tc["login"],
                name=tc["name"],
                project_key=tc.get("project_key"),
                project_name=tc.get("project_name"),
            )
            for tc in top_contributors
        ]
