"""OWASP repository contributor GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.repository_contributor import RepositoryContributorNode
from apps.github.models.repository_contributor import RepositoryContributor


class RepositoryContributorQuery(BaseQuery):
    """Repository contributor queries."""

    top_contributors = graphene.List(
        RepositoryContributorNode,
        limit=graphene.Int(default_value=15),
        organization=graphene.String(required=False),
        project=graphene.String(required=False),
        chapter=graphene.String(required=False),
        committee=graphene.String(required=False),
        repository=graphene.String(required=False),
    )

    def resolve_top_contributors(
        root,
        info,
        limit,
        organization=None,
        project=None,
        chapter=None,
        committee=None,
        repository=None,
    ):
        """Resolve top contributors.

        Args:
            root (Any): The root query object.
            info (ResolveInfo): The GraphQL execution context.
            limit (int): Maximum number of contributors to return.
            organization (str, optional): Organization login to filter by.
            project (str, optional): Project key to filter by.
            chapter (str, optional): Chapter key to filter by.
            committee (str, optional): Committee key to filter by.
            repository (str, optional): Repository name to filter by.

        Returns:
            list: List of top contributors with their details.

        """
        top_contributors = RepositoryContributor.get_top_contributors(
            organization=organization,
            project=project,
            chapter=chapter,
            committee=committee,
            repository=repository,
            limit=limit,
        )

        return [
            RepositoryContributorNode(
                avatar_url=trc["avatar_url"],
                contributions_count=trc["contributions_count"],
                login=trc["login"],
                name=trc["name"],
                project_key=trc["project_key"],
                project_name=trc["project_name"],
            )
            for trc in top_contributors
        ]
