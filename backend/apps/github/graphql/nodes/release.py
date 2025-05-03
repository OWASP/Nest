"""GitHub release GraphQL node."""

from __future__ import annotations

import graphene

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.user import UserNode
from apps.github.models.release import Release
from apps.owasp.constants import OWASP_ORGANIZATION_NAME


class ReleaseNode(BaseNode):
    """GitHub release node."""

    author = graphene.Field(UserNode)
    organization_name = graphene.String()
    project_name = graphene.String()
    repository_name = graphene.String()
    url = graphene.String()

    class Meta:
        model = Release
        fields = (
            "author",
            "is_pre_release",
            "name",
            "published_at",
            "tag_name",
        )

    def resolve_organization_name(self, info) -> str | None:
        """Return organization name."""
        return self.repository.organization.login if self.repository.organization else None

    def resolve_project_name(self, info) -> str:
        """Return project name."""
        return self.repository.project.name.lstrip(OWASP_ORGANIZATION_NAME)

    def resolve_repository_name(self, info) -> str:
        """Return repository name."""
        return self.repository.name

    def resolve_url(self, info) -> str:
        """Return release URL."""
        return self.url
