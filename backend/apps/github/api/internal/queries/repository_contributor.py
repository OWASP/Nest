"""OWASP repository contributor GraphQL queries."""

import strawberry

from apps.github.api.internal.nodes.repository_contributor import RepositoryContributorNode
from apps.github.models.repository_contributor import RepositoryContributor


@strawberry.type
class RepositoryContributorQuery:
    """Repository contributor queries."""

    @strawberry.field
    def top_contributors(
        self,
        limit: int = 24,
        chapter: str | None = None,
        committee: str | None = None,
        excluded_usernames: list[str] | None = None,
        organization: str | None = None,
        project: str | None = None,
        repository: str | None = None,
    ) -> list[RepositoryContributorNode]:
        """Resolve top contributors.

        Args:
            limit (int): Maximum number of contributors to return.
            chapter (str, optional): Chapter key to filter by.
            committee (str, optional): Committee key to filter by.
            organization (str, optional): Organization login to filter by.
            excluded_usernames (list[str], optional): Usernames to exclude from the results.
            project (str, optional): Project key to filter by.
            repository (str, optional): Repository name to filter by.

        Returns:
            list: List of top contributors with their details.

        """
        top_contributors = RepositoryContributor.get_top_contributors(
            limit=limit,
            chapter=chapter,
            committee=committee,
            excluded_usernames=excluded_usernames,
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
