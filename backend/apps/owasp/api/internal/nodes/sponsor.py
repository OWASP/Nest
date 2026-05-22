"""OWASP sponsors GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.models.sponsor import Sponsor


@strawberry_django.type(
    Sponsor,
    fields=["image_url", "name", "sponsor_type", "url", "description"],
)
class SponsorNode(strawberry.relay.Node):
    """Sponsor node."""


@strawberry.input
class CreateSponsorInput:
    """Input Node for creating a sponsor."""

    message: str
    name: str
    url: str
    contact_email: str
