"""Github Milestone Node."""

import graphene

from apps.common.graphql.nodes import BaseNode
from apps.github.models.milestone import Milestone


class MilestoneNode(BaseNode):
    """Github Milestone Node."""

    organization_name = graphene.String()
    progress = graphene.Float()
    repository_name = graphene.String()

    class Meta:
        model = Milestone

        fields = (
            "author",
            "body",
            "created_at",
            "title",
            "open_issues_count",
            "closed_issues_count",
            "url",
        )

    def resolve_organization_name(self, info):
        """Return organization name."""
        return self.repository.organization.login if self.repository.organization else None

    def resolve_progress(self, info):
        """Return milestone progress."""
        total_issues_count = self.closed_issues_count + self.open_issues_count
        if not total_issues_count:
            return 0
        return round(self.closed_issues_count / total_issues_count, 2) * 100

    def resolve_repository_name(self, info):
        """Resolve repository name."""
        return self.repository.name
