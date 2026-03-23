import logging

import strawberry
from django.utils import timezone

from apps.common.utils import slugify
from apps.owasp.api.internal.nodes.sponsor import CreateSponsorInput, SponsorNode
from apps.owasp.models import Sponsor

logger = logging.getLogger(__name__)


@strawberry.type
class SponsorMutation:
    """GraphQL mutations related to sponsor."""

    @strawberry.mutation
    def create_sponsor(self, input_data: CreateSponsorInput) -> SponsorNode:
        """Create a new sponsor."""

        sponsor = Sponsor.objects.create(
            key=slugify(input_data.name),
            sort_name=input_data.name,
            name=input_data.name,
            contact_email=input_data.contact_email,
            message=input_data.message,
            url=input_data.url,
            created_at=timezone.now(),
        )

        logger.info("Sponsor created successfully")

        return sponsor
