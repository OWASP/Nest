"""OWASP app sponsor models."""

from __future__ import annotations

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.common.utils import slugify
from apps.github.utils import normalize_url


class Sponsor(BulkSaveModel, TimestampedModel):
    """Sponsor model."""

    objects = models.Manager()

    class Meta:
        """Model options."""

        db_table = "owasp_sponsors"
        verbose_name_plural = "Sponsors"

    class SponsorType(models.TextChoices):
        """Sponsor type choices."""

        DIAMOND = "Diamond"
        PLATINUM = "Platinum"
        GOLD = "Gold"
        SILVER = "Silver"
        SUPPORTER = "Supporter"
        NOT_SPONSOR = "Not a Sponsor"

    class MemberType(models.TextChoices):
        """Member type choices."""

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

    def __str__(self) -> str:
        """Sponsor human readable representation."""
        return f"{self.name}"

    @property
    def readable_member_type(self) -> str:
        """Get human-readable member type."""
        return self.MemberType(self.member_type).label

    @property
    def readable_sponsor_type(self) -> str:
        """Get human-readable sponsor type."""
        return self.SponsorType(self.sponsor_type).label

    @staticmethod
    def bulk_save(  # type: ignore[override]
        sponsors: list[Sponsor],
        fields: tuple[str, ...] | None = None,
    ) -> None:
        """Bulk save sponsors.

        Args:
            sponsors (list[Sponsor]): List of Sponsor instances to save.
            fields (tuple[str], optional): Tuple of fields to update.

        """
        BulkSaveModel.bulk_save(Sponsor, sponsors, fields=fields)

    @staticmethod
    def update_data(data: dict, *, save: bool = True) -> Sponsor:
        """Update sponsor data.

        Args:
            data (dict): Dictionary containing sponsor data.
            save (bool, optional): Whether to save the instance.

        Returns:
            Sponsor: The updated Sponsor instance.

        """
        key = slugify(data["name"])
        try:
            sponsor = Sponsor.objects.get(key=key)
        except Sponsor.DoesNotExist:
            sponsor = Sponsor(key=key)

        sponsor.from_dict(data)

        if save:
            sponsor.save()

        return sponsor

    def from_dict(self, data: dict) -> None:
        """Update instance based on the dictionary data.

        Args:
            data (dict): Dictionary containing sponsor data.

        """
        image_path = data.get("image", "").lstrip("/")
        image_url = f"https://raw.githubusercontent.com/OWASP/owasp.github.io/main/{image_path}"

        member_type_mapping = {
            2: self.MemberType.PLATINUM,
            3: self.MemberType.GOLD,
            4: self.MemberType.SILVER,
        }
        sponsor_type_mapping = {
            -1: self.SponsorType.NOT_SPONSOR,
            1: self.SponsorType.DIAMOND,
            2: self.SponsorType.PLATINUM,
            3: self.SponsorType.GOLD,
            4: self.SponsorType.SILVER,
            5: self.SponsorType.SUPPORTER,
        }

        member_key = data.get("membertype", 4)
        sponsor_key = data.get("sponsor", -1)
        member_type_label = member_type_mapping.get(member_key, self.MemberType.SILVER)
        sponsor_type_label = sponsor_type_mapping.get(sponsor_key, self.SponsorType.NOT_SPONSOR)

        fields = {
            "description": data.get("description", ""),
            "image_url": image_url,
            "is_member": data.get("member", False),
            "job_url": normalize_url(data.get("job_url", "")) or "",
            "member_type": member_type_label,
            "name": data["name"],
            "sort_name": data.get("sortname", ""),
            "sponsor_type": sponsor_type_label,
            "url": normalize_url(data.get("url", "")) or "",
        }

        for key, value in fields.items():
            setattr(self, key, value)
