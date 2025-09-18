"""OWASP user GraphQL queries."""

import strawberry

from apps.github.api.internal.nodes.repository import RepositoryNode
from apps.github.api.internal.nodes.user import UserNode
from apps.github.models.repository_contributor import RepositoryContributor
from apps.github.models.user import User


@strawberry.type
class UserQuery:
    """User queries."""

    @strawberry.field
    def top_contributed_repositories(
        self,
        login: str,
    ) -> list[RepositoryNode]:
        """Resolve user top repositories.

        Args:
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
        login: str,
    ) -> UserNode | None:
        """Resolve user by login.

        Args:
            login (str): The login of the user.

        Returns:
            User or None: The user object if found, otherwise None.

        """
        return User.objects.filter(has_public_member_page=True, login=login).first()
