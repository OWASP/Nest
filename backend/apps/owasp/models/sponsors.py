"""OWASP app sponsor models."""

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.common.utils import slugify
from apps.github.utils import normalize_url
from apps.owasp.constants import OWASP_ORGANIZATION_DATA_URL


class Sponsor(BulkSaveModel, TimestampedModel):
    """Sponsor model."""

    objects = models.Manager()

    class Meta:
        db_table = "owasp_sponsors"
        verbose_name_plural = "Sponsors"

    class SponsorType(models.TextChoices):
        DIAMOND = "Diamond"
        PLATINUM = "Platinum"
        GOLD = "Gold"
        SILVER = "Silver"
        SUPPORTER = "Supporter"
        NOT_SPONSOR = "Not a Sponsor"

    class MemberType(models.TextChoices):
        PLATINUM = "Platinum"
        GOLD = "Gold"
        SILVER = "Silver"

    # Basic information
    description = models.TextField(verbose_name="Description", blank=True)
    key = models.CharField(verbose_name="Key", max_length=100, unique=True)
    name = models.CharField(verbose_name="Name", max_length=255)
    sort_name = models.CharField(verbose_name="Sort Name", max_length=255)

    # URLs and images
    url = models.URLField(verbose_name="Website URL", blank=True)
    job_url = models.URLField(verbose_name="Job URL", blank=True)
    image_url = models.CharField(verbose_name="Image Path", max_length=255, blank=True)

    # Status fields
    is_member = models.BooleanField(verbose_name="Is Corporate Sponsor", default=False)
    member_type = models.CharField(
        verbose_name="Member Type",
        max_length=20,
        choices=MemberType.choices,
        default=MemberType.SILVER,
        blank=True,
    )
    sponsor_type = models.CharField(
        verbose_name="Sponsor Type",
        max_length=20,
        choices=SponsorType.choices,
        default=SponsorType.NOT_SPONSOR,
    )

    def __str__(self):
        """Sponsor human readable representation."""
        return f"{self.name}"

    @property
    def readable_member_type(self):
        """Get human-readable member type."""
        return self.MemberType(str(self.member_type)).label

    @property
    def readable_sponsor_type(self):
        """Get human-readable sponsor type."""
        return self.SponsorType(str(self.sponsor_type)).label

    @staticmethod
    def bulk_save(sponsors, fields=None):
        """Bulk save sponsors."""
        BulkSaveModel.bulk_save(Sponsor, sponsors, fields=fields)

    @staticmethod
    def update_data(data, save=True):
        """Update sponsor data."""
        key = slugify(data["name"])
        try:
            sponsor = Sponsor.objects.get(key=key)
        except Sponsor.DoesNotExist:
            sponsor = Sponsor(key=key)

        sponsor.from_dict(data)
        if save:
            sponsor.save()

        return sponsor

    def from_dict(self, data):
        """Update instance based on the dict data."""
        image_path = data.get("image", "").lstrip("/")
        image_url = f"{OWASP_ORGANIZATION_DATA_URL}/{image_path}"

        member_type_mapping = {
            "2": self.MemberType.PLATINUM,
            "3": self.MemberType.GOLD,
            "4": self.MemberType.SILVER,
        }

        sponsor_type_mapping = {
            "1": self.SponsorType.DIAMOND,
            "2": self.SponsorType.PLATINUM,
            "3": self.SponsorType.GOLD,
            "4": self.SponsorType.SILVER,
            "5": self.SponsorType.SUPPORTER,
            "-1": self.SponsorType.NOT_SPONSOR,
        }

        sponsor_type_label = sponsor_type_mapping.get(
            data.get("sponsor", "-1") or "-1", self.SponsorType.NOT_SPONSOR
        )
        member_type_label = member_type_mapping.get(
            data.get("membertype", "4") or "4", self.MemberType.SILVER
        )

        fields = {
            "name": data.get("name", ""),
            "sort_name": data.get("sortname", "").capitalize(),
            "description": data.get("description", ""),
            "url": normalize_url(data.get("url", "")) or "",
            "job_url": normalize_url(data.get("job_url", "")) or "",
            "image_url": image_url,
            "is_member": data.get("member", False),
            "sponsor_type": sponsor_type_label,
            "member_type": member_type_label,
        }

        for key, value in fields.items():
            setattr(self, key, value)
