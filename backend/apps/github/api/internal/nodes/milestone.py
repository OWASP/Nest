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

    @strawberry_django.field
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
    def progress(self) -> float:
        """Resolve milestone progress."""
        total_issues_count = self.closed_issues_count + self.open_issues_count
        if not total_issues_count:
            return 0.0
        return round((self.closed_issues_count / total_issues_count) * 100, 2)

    @strawberry.field
    def repository_name(self) -> str | None:
        """Resolve repository name."""
        return self.repository.name if self.repository else None
