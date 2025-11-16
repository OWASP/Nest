"""GitHub Pull Request Node."""

import strawberry
import strawberry_django

from apps.github.api.internal.nodes.user import UserNode
from apps.github.models.pull_request import PullRequest


@strawberry_django.type(
    PullRequest,
    fields=[
        "created_at",
        "title",
        "state",
        "merged_at",
    ],
)
class PullRequestNode(strawberry.relay.Node):
    """GitHub pull request node."""

    @strawberry.field
    def author(self) -> UserNode | None:
        """Resolve author."""
        return self.author

    @strawberry.field
    def organization_name(self) -> str | None:
        """Resolve organization name."""
        return (
            self.repository.organization.login
            if self.repository and self.repository.organization
            else None
        )

    @strawberry.field
    def repository_name(self) -> str | None:
        """Resolve repository name."""
        return self.repository.name if self.repository else None

    @strawberry.field
    def url(self) -> str:
        """Resolve URL."""
        return str(self.url) if self.url else ""
