"""OWASP sponsors GraphQL node."""

import strawberry_django

from apps.owasp.models.sponsor import Sponsor


@strawberry_django.type(
    Sponsor,
    fields=[
        "image_url",
        "name",
        "sponsor_type",
        "url",
    ],
)
class SponsorNode:
    """Sponsor node."""
