"""GitHub issue GraphQL node."""

import strawberry
import strawberry_django

from apps.github.api.internal.nodes.pull_request import PullRequestNode
from apps.github.api.internal.nodes.user import UserNode
from apps.github.models.issue import Issue


@strawberry_django.type(
    Issue,
    fields=[
        "body",
        "created_at",
        "number",
        "state",
        "title",
        "url",
    ],
)
class IssueNode(strawberry.relay.Node):
    """GitHub issue node."""

    author: UserNode | None = strawberry_django.field()
    assignees: list[UserNode] = strawberry_django.field()
    pull_requests: list[PullRequestNode] = strawberry_django.field()

    @strawberry_django.field(select_related=["repository__organization", "repository"])
    def organization_name(self, root: Issue) -> str | None:
        """Resolve organization name."""
        return (
            root.repository.organization.login
            if root.repository and root.repository.organization
            else None
        )

    @strawberry_django.field(select_related=["repository"])
    def repository_name(self, root: Issue) -> str | None:
        """Resolve the repository name."""
        return root.repository.name if root.repository else None

    @strawberry_django.field(prefetch_related=["labels"])
    def labels(self, root: Issue) -> list[str]:
        """Resolve label names for the issue."""
        return list(root.labels.values_list("name", flat=True))

    @strawberry_django.field(prefetch_related=["pull_requests"])
    def is_merged(self, root: Issue) -> bool:
        """Return True if this issue has at least one merged pull request."""
        return root.pull_requests.filter(state="closed", merged_at__isnull=False).exists()

    @strawberry_django.field(prefetch_related=["participant_interests"])
    def interested_users(self, root: Issue) -> list[UserNode]:
        """Return all users who have expressed interest in this issue."""
        return [
            interest.user
            for interest in root.participant_interests.select_related("user").order_by(
                "user__login"
            )
        ]
