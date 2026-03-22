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

    author: UserNode | None = strawberry_django.field()

    @strawberry_django.field(select_related=["repository__organization"])
    def organization_name(self, root: Release) -> str | None:
        """Resolve organization name."""
        return (
            root.repository.organization.login
            if root.repository and root.repository.organization
            else None
        )

    @strawberry_django.field(
        select_related=["repository"], prefetch_related=["repository__project_set"]
    )
    def project_name(self, root: Release) -> str | None:
        """Resolve project name."""
        return (
            root.repository.project.name.lstrip(OWASP_ORGANIZATION_NAME)
            if root.repository and root.repository.project
            else None
        )

    @strawberry_django.field(select_related=["repository"])
    def repository_name(self, root: Release) -> str | None:
        """Resolve repository name."""
        return root.repository.name if root.repository else None

    @strawberry_django.field
    def url(self, root: Release) -> str:
        """Resolve URL."""
        return root.url
