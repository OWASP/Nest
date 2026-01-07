"""GitHub release GraphQL node."""

import strawberry
import strawberry_django

from apps.github.api.internal.nodes.user import UserNode
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
class ReleaseNode(strawberry.relay.Node):
    """GitHub release node."""

    @strawberry_django.field
    def author(self) -> UserNode | None:
        """Resolve author."""
        return self.author

    @strawberry_django.field
    def organization_name(self) -> str | None:
        """Resolve organization name."""
        return (
            self.repository.organization.login
            if self.repository and self.repository.organization
            else None
        )

    @strawberry_django.field
    def project_name(self) -> str | None:
        """Resolve project name."""
        return (
            self.repository.project.name.lstrip(OWASP_ORGANIZATION_NAME)
            if self.repository and self.repository.project
            else None
        )

    @strawberry_django.field
    def repository_name(self) -> str | None:
        """Resolve repository name."""
        return self.repository.name if self.repository else None

    @strawberry_django.field
    def url(self) -> str:
        """Resolve URL."""
        return self.url
