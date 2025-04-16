"""GitHub release GraphQL node."""

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

    def resolve_organization_name(self, info):
        """Return organization name."""
        if self.repository.organization:
            return self.repository.organization.login
        return None

    def resolve_project_name(self, info):
        """Return project name."""
        return self.repository.project.name.lstrip(OWASP_ORGANIZATION_NAME)

    def resolve_repository_name(self, info):
        """Return repository name."""
        return self.repository.name

    def resolve_url(self, info):
        """Return release URL."""
        return self.url
