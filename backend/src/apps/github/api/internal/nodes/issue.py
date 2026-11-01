"""GitHub issue GraphQL node."""

from datetime import datetime

import strawberry
import strawberry_django
from django.db.models import Prefetch
from strawberry.types import Info

from apps.common.utils import normalize_limit
from apps.github.api.internal.nodes.pull_request import PullRequestNode
from apps.github.api.internal.nodes.user import UserNode
from apps.github.models.issue import Issue
from apps.github.models.pull_request import PullRequest
from apps.mentorship.models.issue_user_interest import IssueUserInterest
from apps.mentorship.models.task import Task

MERGED_PULL_REQUESTS_PREFETCH = Prefetch(
    "pull_requests",
    queryset=PullRequest.objects.filter(
        merged_at__isnull=False,
        state="closed",
    ),
    to_attr="merged_pull_requests",
)

MAX_LIMIT = 1000


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

    @strawberry_django.field(prefetch_related=["pull_requests"])
    def pull_requests(self, limit: int = 4, offset: int = 0) -> list[PullRequestNode]:
        """Return pull requests linked to this issue."""
        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            return []

        offset = max(0, offset)
        return list(
            self.pull_requests.all().order_by("-created_at")[offset : offset + normalized_limit]
        )

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
        return bool(getattr(root, "merged_pull_requests", None))

    @strawberry_django.field(
        prefetch_related=[
            Prefetch(
                "participant_interests",
                queryset=IssueUserInterest.objects.select_related("user__owasp_profile").order_by(
                    "user__login"
                ),
                to_attr="interests_users",
            )
        ]
    )
    def interested_users(self, root: Issue) -> list[UserNode]:
        """Return all users who have expressed interest in this issue."""
        return [interest.user for interest in getattr(root, "interests_users", [])]

    @strawberry.field
    def task_deadline(self, root: Issue, info: Info) -> datetime | None:
        """Return the deadline for the latest assigned task linked to this issue."""
        mapping = getattr(info.context, "task_deadlines_by_issue", None)
        if mapping is not None:
            return mapping.get(root.number)

        return (
            Task.objects.filter(
                issue=root,
                deadline_at__isnull=False,
            )
            .order_by("-assigned_at")
            .values_list("deadline_at", flat=True)
            .first()
        )
