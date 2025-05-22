"""Github Milestone Node."""

import strawberry
import strawberry_django

from apps.github.graphql.nodes.user import UserNode
from apps.github.models.milestone import Milestone


@strawberry_django.type(
    Milestone,
    fields=[
        "closed_issues_count",
        "created_at",
        "open_issues_count",
        "title",
        "url",
    ],
)
class MilestoneNode:
    """Github Milestone Node."""

    @strawberry.field
    def author(self) -> UserNode | None:
        """Resolve author."""
        return self.author

    @strawberry.field
    def organization_name(self) -> str | None:
        """Return organization name."""
        return (
            self.repository.organization.login
            if self.repository and self.repository.organization
            else None
        )

    @strawberry.field
    def repository_name(self) -> str | None:
        """Resolve repository name."""
        return self.repository.name if self.repository else None
