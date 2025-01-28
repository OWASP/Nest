"""OWASP app sponsor models."""

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.owasp.models.mixins.sponsor import SponsorIndexMixin


class Sponsor(BulkSaveModel, SponsorIndexMixin, TimestampedModel):
    """Sponsor model."""

    objects = models.Manager()

    class Meta:
        db_table = "owasp_sponsors"
        verbose_name_plural = "Sponsors"

    class SponsorType(models.TextChoices):
        DIAMOND = "1", "Diamond"
        PLATINUM = "2", "Platinum"
        GOLD = "3", "Gold"
        SILVER = "4", "Silver"
        SUPPORTER = "5", "Supporter"
        NOT_SPONSOR = "-1", "Not a Sponsor"

    class MemberType(models.TextChoices):
        PLATINUM = "2", "Platinum"
        GOLD = "3", "Gold"
        SILVER = "4", "Silver"

    # Basic information
    name = models.CharField(verbose_name="Name", max_length=255)
    sort_name = models.CharField(verbose_name="Sort Name", max_length=255)
    description = models.TextField(verbose_name="Description", blank=True)

    # URLs and images
    url = models.URLField(verbose_name="Website URL", blank=True)
    job_url = models.URLField(verbose_name="Job URL", blank=True)
    image_path = models.CharField(verbose_name="Image Path", max_length=255, blank=True)

    # Status fields
    is_member = models.BooleanField(verbose_name="Is Corporate Sponsor", default=False)
    member_type = models.CharField(
        verbose_name="Member Type",
        max_length=2,
        choices=MemberType.choices,
        default=MemberType.SILVER,
        blank=True,
    )
    sponsor_type = models.CharField(
        verbose_name="Sponsor Type",
        max_length=2,
        choices=SponsorType.choices,
        default=SponsorType.NOT_SPONSOR,
    )

    def __str__(self):
        """Sponsor human readable representation."""
        return f"{self.name}"

    @property
    def readable_sponsor_type(self):
        """Get human-readable sponsor type."""
        return self.SponsorType(str(self.sponsor_type)).label

    @property
    def readable_member_type(self):
        """Get human-readable member type."""
        return self.MemberType(str(self.member_type)).label

    @property
    def is_indexable(self):
        """Determine if the sponsor should be indexed in Algolia."""
        return True

    @staticmethod
    def bulk_save(sponsors, fields=None):
        """Bulk save sponsors."""
        BulkSaveModel.bulk_save(Sponsor, sponsors, fields=fields)

    @staticmethod
    def update_data(sponsor_id, **kwargs):
        """Update sponsor data."""
        try:
            sponsor = Sponsor.objects.get(id=sponsor_id)
            for key, value in kwargs.items():
                setattr(sponsor, key, value)
            sponsor.save()
        except Sponsor.DoesNotExist:
            return None
        else:
            return sponsor
