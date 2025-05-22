"""OWASP user GraphQL queries."""

import strawberry

from apps.github.graphql.nodes.repository import RepositoryNode
from apps.github.graphql.nodes.user import UserNode
from apps.github.models.repository_contributor import RepositoryContributor
from apps.github.models.user import User


@strawberry.type
class UserQuery:
    """User queries."""

    @strawberry.field
    def top_contributed_repositories(
        self,
        info,
        login: str,
    ) -> list[RepositoryNode]:
        """Resolve user top repositories.

        Args:
            info (ResolveInfo): The GraphQL execution context.
            login (str): The login of the user.

        Returns:
            list: List of repositories the user has contributed to.

        """
        return [
            rc.repository
            for rc in RepositoryContributor.objects.select_related(
                "repository",
                "repository__organization",
            )
            .filter(user__login=login)
            .order_by("-contributions_count")
        ]

    @strawberry.field
    def user(
        self,
        info,
        login: str,
    ) -> UserNode | None:
        """Resolve user by login.

        Args:
            info (ResolveInfo): The GraphQL execution context.
            login (str): The login of the user.

        Returns:
            User or None: The user object if found, otherwise None.

        """
        try:
            return User.objects.get(login=login)
        except User.DoesNotExist:
            return None
