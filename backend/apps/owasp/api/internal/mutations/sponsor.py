"""OWASP sponsors GraphQL mutations."""

import logging

import strawberry
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from apps.common.utils import slugify
from apps.owasp.api.internal.nodes.sponsor import SponsorNode
from apps.owasp.models.sponsor import Sponsor

logger = logging.getLogger(__name__)


@strawberry.type
class CreateSponsorApplicationResult:
    """Result of creating a sponsor application."""

    ok: bool
    sponsor: SponsorNode | None = None
    code: str | None = None
    message: str | None = None


@strawberry.type
class SponsorMutations:
    """Sponsor mutations."""

    @strawberry.mutation
    def create_sponsor_application(
        self,
        name: str,
        contact_email: str,
        sponsorship_interest: str,
        website: str | None = None,
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

        try:
            name_clean = name.strip()
            email_clean = contact_email.strip()
            interest_clean = sponsorship_interest.strip()
            url_clean = website.strip() if website else ""
            key = slugify(name_clean)

            # Validate before get_or_create to avoid saving invalid sponsor
            temp_sponsor = Sponsor(
                name=name_clean,
                contact_email=email_clean,
                url=url_clean,
                description=interest_clean,
                status=Sponsor.Status.DRAFT,
                sort_name=name_clean,
                key=key,
            )
            temp_sponsor.full_clean(validate_unique=False)

            sponsor, created = Sponsor.objects.get_or_create(
                key=key,
                defaults={
                    "name": name_clean,
                    "contact_email": email_clean,
                    "url": url_clean,
                    "description": interest_clean,
                    "status": Sponsor.Status.DRAFT,
                    "sort_name": name_clean,
                },
            )

            if not created:
                return CreateSponsorApplicationResult(
                    ok=False,
                    code="DUPLICATE",
                    message="A sponsor with this organization name already exists",
                )

            logger.info("Sponsor application created: %s - %s", sponsor.id, sponsor.name)

            return CreateSponsorApplicationResult(
                ok=True,
                sponsor=sponsor,
                code="SUCCESS",
                message="Sponsor application submitted successfully",
            )

        except (ValidationError, IntegrityError) as err:
            logger.warning("Error creating sponsor application: %s", err)
            return CreateSponsorApplicationResult(
                ok=False,
                code="ERROR",
                message="Error submitting sponsor application",
            )
