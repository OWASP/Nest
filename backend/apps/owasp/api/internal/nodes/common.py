"""OWASP common GraphQL node."""

import strawberry
import strawberry_django
from django.contrib.contenttypes.prefetch import GenericPrefetch
from django.db.models import Prefetch

from apps.github.api.internal.nodes.repository_contributor import RepositoryContributorNode
from apps.owasp.api.internal.nodes.entity_channel import EntityChannelNode
from apps.owasp.api.internal.nodes.entity_member import EntityMemberNode
from apps.owasp.models.entity_channel import EntityChannel
from apps.slack.models.conversation import Conversation

ENTITY_CHANNELS_PREFETCH = Prefetch(
    "entity_channels",
    queryset=EntityChannel.objects.filter(is_active=True).prefetch_related(
        GenericPrefetch("channel", [Conversation.objects.all()]),
    ),
)


@strawberry.type
class GenericEntityNode(strawberry.relay.Node):
    """Base node class for OWASP entities with common fields and resolvers."""

    @strawberry_django.field(prefetch_related=["entity_members__member"])
    def entity_leaders(self, root) -> list[EntityMemberNode]:
        """Resolve entity leaders."""
        return root.entity_leaders

    @strawberry_django.field(prefetch_related=[ENTITY_CHANNELS_PREFETCH])
    def entity_channels(self, root) -> list[EntityChannelNode]:
        """Resolve entity channels."""
        return list(root.entity_channels.all())

    @strawberry_django.field
    def leaders(self, root) -> list[str]:
        """Resolve leaders."""
        return root.idx_leaders

    @strawberry_django.field
    def related_urls(self, root) -> list[str]:
        """Resolve related URLs."""
        return root.related_urls

    @strawberry_django.field
    def top_contributors(self, root) -> list[RepositoryContributorNode]:
        """Resolve top contributors."""
        return [RepositoryContributorNode(**tc) for tc in root.idx_top_contributors]

    @strawberry_django.field
    def updated_at(self, root) -> float:
        """Resolve updated at."""
        return root.idx_updated_at

    @strawberry_django.field
    def url(self, root) -> str:
        """Resolve URL."""
        return root.idx_url
