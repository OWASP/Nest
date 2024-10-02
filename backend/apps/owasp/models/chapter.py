"""OWASP app chapter model."""

from django.db import models
from geopy.geocoders import Nominatim

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.common.utils import get_nest_user_agent, join_values
from apps.owasp.models.common import OwaspEntity
from apps.owasp.models.managers.chapter import ActiveChaptertManager


class Chapter(BulkSaveModel, OwaspEntity, TimestampedModel):
    """Chapter model."""

    objects = models.Manager()
    active_chapters = ActiveChaptertManager()

    class Meta:
        db_table = "owasp_chapters"
        verbose_name_plural = "Chapters"

    name = models.CharField(verbose_name="Name", max_length=100)
    key = models.CharField(verbose_name="Key", max_length=100, unique=True)
    level = models.CharField(verbose_name="Level", max_length=5, default="")

    country = models.CharField(verbose_name="Country", max_length=50, default="")
    region = models.CharField(verbose_name="Region", max_length=50, default="")
    postal_code = models.CharField(verbose_name="Postal code", max_length=15, default="")
    currency = models.CharField(verbose_name="Currency", max_length=10, default="")
    meetup_group = models.CharField(verbose_name="Meetup group", max_length=100, default="")

    latitude = models.FloatField(verbose_name="Latitude", blank=True, null=True)
    longitude = models.FloatField(verbose_name="Longitude", blank=True, null=True)

    tags = models.JSONField(verbose_name="Tags", default=list)

    owasp_repository = models.ForeignKey(
        "github.Repository", on_delete=models.SET_NULL, blank=True, null=True
    )

    def __str__(self):
        """Chapter human readable representation."""
        return f"{self.name or self.key}"

    @property
    def geo_string(self):
        """Return geo string."""
        return join_values(
            (
                self.name.replace("OWASP", "").strip(),
                self.country,
                self.postal_code,
            ),
            delimiter=", ",
        )

    def from_github(self, repository):
        """Update instance based on GitHub repository data."""
        field_mapping = {
            "country": "country",
            "currency": "currency",
            "level": "level",
            "meetup_group": "meetup-group",
            "name": "title",
            "postal_code": "postal-code",
            "region": "region",
            "tags": "tags",
        }
        OwaspEntity.from_github(self, field_mapping, repository)

        # FKs.
        self.owasp_repository = repository

    def generate_geo_location(self, geo_locator=None):
        """Add latitude and longitude data."""
        geo_locator = geo_locator or Nominatim(user_agent=get_nest_user_agent())
        location = geo_locator.geocode(self.geo_string)
        if location:
            self.latitude = location.latitude
            self.longitude = location.longitude

    def save(self, *args, **kwargs):
        """Save chapter."""
        if not self.latitude or not self.longitude:
            self.generate_geo_location()

        super().save(*args, **kwargs)

    @staticmethod
    def bulk_save(chapters, fields=None):
        """Bulk save chapters."""
        BulkSaveModel.bulk_save(Chapter, chapters, fields=fields)

    @staticmethod
    def update_data(gh_repository, repository, save=True):
        """Update chapter data."""
        key = gh_repository.name.lower()
        try:
            chapter = Chapter.objects.get(key=key)
        except Chapter.DoesNotExist:
            chapter = Chapter(key=key)

        chapter.from_github(repository)
        if save:
            chapter.save()

        return chapter
