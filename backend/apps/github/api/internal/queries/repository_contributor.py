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
        *,
        chapter: str | None = None,
        committee: str | None = None,
        excluded_usernames: list[str] | None = None,
        has_full_name: bool = False,
        limit: int = 24,
        organization: str | None = None,
        project: str | None = None,
        repository: str | None = None,
    ) -> list[RepositoryContributorNode]:
        """Resolve top contributors.

        Args:
            chapter (str, optional): Chapter key to filter by.
            committee (str, optional): Committee key to filter by.
            excluded_usernames (list[str], optional): Usernames to exclude from the results.
            has_full_name (bool, optional): Filter contributors with likely full names.
            limit (int, optional): Maximum number of contributors to return.
            organization (str, optional): Organization login to filter by.
            project (str, optional): Project key to filter by.
            repository (str, optional): Repository name to filter by.

        Returns:
            list: List of top contributors with their details.

        """
        if limit <= 0:
            return []
        top_contributors = RepositoryContributor.get_top_contributors(
            chapter=chapter,
            committee=committee,
            excluded_usernames=excluded_usernames,
            has_full_name=has_full_name,
            limit=limit,
            organization=organization,
            project=project,
            repository=repository,
        )

        return [
            RepositoryContributorNode(
                avatar_url=tc["avatar_url"],
                contributions_count=tc["contributions_count"],
                id=tc["login"],
                login=tc["login"],
                name=tc["name"],
                project_key=tc.get("project_key"),
                project_name=tc.get("project_name"),
            )
            for tc in top_contributors
        ]
