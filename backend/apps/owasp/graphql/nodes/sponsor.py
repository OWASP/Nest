"""OWASP sponsors GraphQL node."""

from apps.common.graphql.nodes import BaseNode
from apps.owasp.models.sponsor import Sponsor


class SponsorNode(BaseNode):
    """Sponsor node."""

    class Meta:
        model = Sponsor
        fields = (
            "image_url",
            "name",
            "url",
        )
