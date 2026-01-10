"""GitHub Pull Request Node."""

import strawberry
import strawberry_django

from apps.github.api.internal.nodes.user import UserNode
from apps.github.models.pull_request import PullRequest


@strawberry_django.type(
    PullRequest,
    fields=[
        "created_at",
        "merged_at",
        "state",
        "title",
    ],
)
class PullRequestNode(strawberry.relay.Node):
    """GitHub pull request node."""

    author: UserNode | None = strawberry_django.field()

    @strawberry_django.field(select_related=["repository__organization"])
    def organization_name(self, root: PullRequest) -> str | None:
        """Resolve organization name."""
        return (
            root.repository.organization.login
            if root.repository and root.repository.organization
            else None
        )

    @strawberry_django.field(select_related=["repository"])
    def repository_name(self, root: PullRequest) -> str | None:
        """Resolve repository name."""
        return root.repository.name if root.repository else None

    @strawberry_django.field
    def url(self, root: PullRequest) -> str:
        """Resolve URL."""
        return str(root.url) if root.url else ""
