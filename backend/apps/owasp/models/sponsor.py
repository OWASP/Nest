"""OWASP app sponsor models."""
from django.db import models
from apps.common.models import BulkSaveModel, TimestampedModel


class Sponsor( BulkSaveModel, TimestampedModel):
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
    url = models.URLField(verbose_name="Website URL", blank=True, null=True)
    job_url = models.URLField(verbose_name="Job URL", blank=True, null=True)
    image = models.CharField(verbose_name="Image Path", max_length=255, blank=True)
    
    # Status fields
    is_member = models.BooleanField(verbose_name="Is Corporate Member", default=False)
    member_type = models.CharField(
        verbose_name="Member Type",
        max_length=2,
        choices=MemberType.choices,
        default=MemberType.SILVER,
        blank=True,
        null=True
    )
    sponsor_type = models.CharField(
        verbose_name="Sponsor Type",
        max_length=2,
        choices=SponsorType.choices,
        default=SponsorType.NOT_SPONSOR,
        null=True
    )
    
    @property
    def idx_created_at(self):
        """Get created timestamp for index."""
        return self.nest_created_at

    @property
    def idx_updated_at(self):
        """Get updated timestamp for index."""
        return self.nest_updated_at

    @property
    def idx_name(self):
        """Get name for index."""
        return self.name

    @property
    def idx_sort_name(self):
        """Get sort name for index."""
        return self.sort_name

    @property
    def idx_description(self):
        """Get description for index."""
        return self.description

    @property
    def idx_url(self):
        """Get URL for index."""
        return self.url

    @property
    def idx_job_url(self):
        """Get job URL for index."""
        return self.job_url

    @property
    def idx_image(self):
        """Get image path for index."""
        return self.image

    @property
    def idx_member_type(self):
        """Get member type for index."""
        return self.member_type

    @property
    def idx_sponsor_type(self):
        """Get sponsor type for index."""
        return self.sponsor_type

    @property
    def idx_member_level(self):
        """Get member level for index."""
        return self.member_level

    @property
    def idx_sponsor_level(self):
        """Get sponsor level for index."""
        return self.sponsor_level

    @property
    def idx_is_member(self):
        """Get member status for index."""
        return self.is_member

    @property
    def idx_is_active_sponsor(self):
        """Get active sponsor status for index."""
        return self.is_active_sponsor
    
    def __str__(self):
        """Sponsor human readable representation."""
        return f"{self.name}"
    
    @property
    def is_active_sponsor(self):
        """Check if the organization is an active sponsor."""
        return self.sponsor_type != self.SponsorType.NOT_SPONSOR
    
    @property
    def sponsor_level(self):
         """Get human-readable sponsor level."""
         return self.SponsorType(str(self.sponsor_type)).label if self.is_active_sponsor else None
    
    @property
    def member_level(self):
        """Get human-readable member level."""
        return self.MemberType(str(self.member_type)).label if self.member_type else None
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
            return sponsor
        except Sponsor.DoesNotExist:
            return None