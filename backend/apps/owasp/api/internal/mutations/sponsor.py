"""OWASP sponsors GraphQL mutations."""

import logging
from typing import Optional

import strawberry
from django.db.utils import IntegrityError

from apps.common.utils import slugify
from apps.owasp.api.internal.nodes.sponsor import SponsorNode
from apps.owasp.models.sponsor import Sponsor

logger = logging.getLogger(__name__)


@strawberry.type
class CreateSponsorApplicationResult:
    """Result of creating a sponsor application."""

    ok: bool
    sponsor: Optional[SponsorNode] = None
    code: Optional[str] = None
    message: Optional[str] = None


@strawberry.type
class SponsorMutations:
    """Sponsor mutations."""

    @strawberry.mutation
    def create_sponsor_application(
        self,
        name: str,
        contact_email: str,
        sponsorship_interest: str,
        website: Optional[str] = None,
    ) -> CreateSponsorApplicationResult:
        """Create a sponsor application.
        
        Args:
            name: Organization name
            contact_email: Contact email address
            sponsorship_interest: Message about sponsorship interest
            website: Organization website (optional)
            
        Returns:
            CreateSponsorApplicationResult with sponsor application status
        """
        try:
            if not name or not name.strip():
                return CreateSponsorApplicationResult(
                    ok=False,
                    code="INVALID_NAME",
                    message="Organization name is required",
                )

            if not contact_email or not contact_email.strip():
                return CreateSponsorApplicationResult(
                    ok=False,
                    code="INVALID_EMAIL",
                    message="Contact email is required",
                )

            if not sponsorship_interest or not sponsorship_interest.strip():
                return CreateSponsorApplicationResult(
                    ok=False,
                    code="INVALID_INTEREST",
                    message="Sponsorship interest message is required",
                )

            key = slugify(name.strip())

            if Sponsor.objects.filter(key=key).exists():
                return CreateSponsorApplicationResult(
                    ok=False,
                    code="DUPLICATE",
                    message="A sponsor with this organization name already exists",
                )

            sponsor = Sponsor(
                name=name.strip(),
                key=key,
                contact_email=contact_email.strip(),
                url=website.strip() if website else "",
                description=sponsorship_interest.strip(),
                status=Sponsor.Status.DRAFT,
                sort_name=name.strip(),
            )
            sponsor.save()

            logger.info(f"Sponsor application created: {sponsor.id} - {sponsor.name}")

            return CreateSponsorApplicationResult(
                ok=True,
                sponsor=sponsor,
                code="SUCCESS",
                message="Sponsor application submitted successfully",
            )

        except IntegrityError as err:
            logger.warning(f"Error creating sponsor application: {err}")
            return CreateSponsorApplicationResult(
                ok=False,
                code="ERROR",
                message="Error submitting sponsor application",
            )
        except Exception as err:
            logger.error(f"Unexpected error creating sponsor application: {err}")
            return CreateSponsorApplicationResult(
                ok=False,
                code="ERROR",
                message="An unexpected error occurred",
            )
