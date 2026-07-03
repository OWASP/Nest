"""OWASP project subscription preference GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.api.internal.nodes.project import ProjectNode
from apps.owasp.models.project_subscription_preference import ProjectSubscriptionPreference


@strawberry_django.type(
    ProjectSubscriptionPreference,
    fields=[
        "include_issues",
        "include_pull_requests",
        "include_releases",
    ],
)
class ProjectSubscriptionPreferenceNode(strawberry.relay.Node):
    """Project subscription preference node."""

    @strawberry_django.field(prefetch_related=["project"])
    def project(self, root: ProjectSubscriptionPreference) -> ProjectNode:
        """Resolve the associated project."""
        return root.project
