"""GitHub release GraphQL node."""

import strawberry
import strawberry_django

from apps.github.graphql.nodes.user import UserNode
from apps.github.models.release import Release
from apps.owasp.constants import OWASP_ORGANIZATION_NAME


@strawberry_django.type(
    Release,
    fields=[
        "is_pre_release",
        "name",
        "published_at",
        "tag_name",
    ],
)
class ReleaseNode:
    """GitHub release node."""

    @strawberry.field
    def author(self) -> UserNode | None:
        """Resolve author."""
        return self.author

    @strawberry.field
    def organization_name(self) -> str | None:
        """Return organization name."""
        return self.repository.organization.login if self.repository.organization else None

    @strawberry.field
    def project_name(self) -> str:
        """Return project name."""
        return self.repository.project.name.lstrip(OWASP_ORGANIZATION_NAME)

    @strawberry.field
    def repository_name(self) -> str:
        """Return repository name."""
        return self.repository.name

    @strawberry.field
    def url(self) -> str:
        """Return release URL."""
        return self.url
