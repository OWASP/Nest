"""GitHub issue GraphQL node."""

import strawberry
import strawberry_django
from django.db.models import Prefetch

from apps.github.api.internal.nodes.pull_request import PullRequestNode
from apps.github.api.internal.nodes.user import UserNode
from apps.github.models.issue import Issue
from apps.github.models.pull_request import PullRequest

MERGED_PULL_REQUESTS_PREFETCH = Prefetch(
    "pull_requests",
    queryset=PullRequest.objects.filter(
        state="closed",
        merged_at__isnull=False,
    ),
    to_attr="merged_pull_requests",
)


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

    assignees: list[UserNode] = strawberry_django.field()
    author: UserNode | None = strawberry_django.field()
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
        return [label.name for label in root.labels.all()]

    @strawberry_django.field(prefetch_related=[MERGED_PULL_REQUESTS_PREFETCH])
    def is_merged(self, root: Issue) -> bool:
        """Return True if this issue has at least one merged pull request."""
        merged = getattr(root, "merged_pull_requests", None)
        if merged is None:
            return False
        return len(merged) > 0

    @strawberry_django.field(prefetch_related=["participant_interests__user"])
    def interested_users(self, root: Issue) -> list[UserNode]:
        """Return all users who have expressed interest in this issue."""
        return [
            interest.user
            for interest in root.participant_interests.select_related("user").order_by(
                "user__login"
            )
        ]
