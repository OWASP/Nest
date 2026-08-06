"""OWASP entity subscription GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.api.internal.nodes.chapter import ChapterNode
from apps.owasp.api.internal.nodes.committee import CommitteeNode
from apps.owasp.api.internal.nodes.project import ProjectNode
from apps.owasp.models.entity_subscription import EntitySubscription


@strawberry_django.type(
    EntitySubscription,
    fields=[
        "frequency",
        "is_active",
        "created_at",
        "updated_at",
    ],
)
class EntitySubscriptionNode(strawberry.relay.Node):
    """Entity subscription node."""

    @strawberry_django.field(select_related=["chapter"])
    def chapter(self, root: EntitySubscription) -> ChapterNode | None:
        """Resolve the associated chapter, if any."""
        return root.chapter

    @strawberry_django.field(select_related=["committee"])
    def committee(self, root: EntitySubscription) -> CommitteeNode | None:
        """Resolve the associated committee, if any."""
        return root.committee

    @strawberry_django.field(select_related=["project"])
    def project(self, root: EntitySubscription) -> ProjectNode | None:
        """Resolve the associated project, if any."""
        return root.project
