"""OWASP entity subscription preference GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.api.internal.nodes.chapter import ChapterNode
from apps.owasp.api.internal.nodes.committee import CommitteeNode
from apps.owasp.api.internal.nodes.project import ProjectNode
from apps.owasp.models.entity_subscription_preference import EntitySubscriptionPreference


@strawberry_django.type(
    EntitySubscriptionPreference,
    fields=[
        "include_issues",
        "include_pull_requests",
        "include_releases",
    ],
)
class EntitySubscriptionPreferenceNode(strawberry.relay.Node):
    """Entity subscription preference node."""

    @strawberry_django.field(select_related=["chapter"])
    def chapter(self, root: EntitySubscriptionPreference) -> ChapterNode | None:
        """Resolve the associated chapter, if any."""
        return root.chapter

    @strawberry_django.field(select_related=["committee"])
    def committee(self, root: EntitySubscriptionPreference) -> CommitteeNode | None:
        """Resolve the associated committee, if any."""
        return root.committee

    @strawberry_django.field(select_related=["project"])
    def project(self, root: EntitySubscriptionPreference) -> ProjectNode | None:
        """Resolve the associated project, if any."""
        return root.project
