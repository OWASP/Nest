"""Github Milestone Node."""

import strawberry
import strawberry_django

from apps.github.api.internal.nodes.user import UserNode
from apps.github.models.milestone import Milestone


@strawberry_django.type(
    Milestone,
    fields=[
        "closed_issues_count",
        "created_at",
        "body",
        "open_issues_count",
        "state",
        "title",
        "url",
    ],
)
class MilestoneNode(strawberry.relay.Node):
    """Github Milestone Node."""

    author: UserNode | None = strawberry_django.field()

    @strawberry_django.field(select_related=["repository__organization"])
    def organization_name(self, root: Milestone) -> str | None:
        """Resolve organization name."""
        return (
            root.repository.organization.login
            if root.repository and root.repository.organization
            else None
        )

    @strawberry_django.field
    def progress(self, root: Milestone) -> float:
        """Resolve milestone progress."""
        total_issues_count = root.closed_issues_count + root.open_issues_count
        if not total_issues_count:
            return 0.0
        return round((root.closed_issues_count / total_issues_count) * 100, 2)

    @strawberry_django.field(select_related=["repository"])
    def repository_name(self, root: Milestone) -> str | None:
        """Resolve repository name."""
        return root.repository.name if root.repository else None
