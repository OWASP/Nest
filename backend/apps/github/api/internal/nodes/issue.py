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
        """Resolve the repository name."""
        return self.repository.name if self.repository else None

    @strawberry.field
    def assignees(self) -> list[UserNode]:
        """Resolve assignees list."""
        return list(self.assignees.all())

    @strawberry.field
    def labels(self) -> list[str]:
        """Resolve label names for the issue."""
        return list(self.labels.values_list("name", flat=True))

    @strawberry.field
    def is_merged(self) -> bool:
        """Return True if this issue has at least one merged pull request."""
        return self.pull_requests.filter(state="closed", merged_at__isnull=False).exists()

    @strawberry.field
    def interested_users(self) -> list[UserNode]:
        """Return all users who have expressed interest in this issue."""
        return [
            interest.user
            for interest in self.participant_interests.select_related("user").order_by(
                "user__login"
            )
        ]

    @strawberry.field
    def pull_requests(self) -> list[PullRequestNode]:
        """Return all pull requests linked to this issue."""
        return list(self.pull_requests.select_related("author", "repository").all())
