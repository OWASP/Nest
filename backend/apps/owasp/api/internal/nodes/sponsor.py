"""OWASP sponsors GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.models.sponsor import Sponsor


@strawberry_django.type(
    Sponsor,
    fields=[
        "description",
        "id",
        "image_url",
        "key",
        "name",
        "sponsor_type",
        "status",
        "url",
    ],
)
class SponsorNode(strawberry.relay.Node):
    """Sponsor node."""
