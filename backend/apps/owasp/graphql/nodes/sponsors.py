"""OWASP sponsors GraphQL node."""

from apps.common.graphql.nodes import BaseNode
from apps.owasp.models.sponsors import Sponsor


class SponsorNode(BaseNode):
    """Sponsor node."""

    class Meta:
        model = Sponsor
        fields = (
            "name",
            "image_url",
        )
