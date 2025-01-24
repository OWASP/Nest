"""OWASP app chapter model."""

from functools import lru_cache

from django.db import models

from apps.common.geocoding import get_location_coordinates
from apps.common.index import IndexBase
from apps.common.models import BulkSaveModel, TimestampedModel
from apps.common.open_ai import OpenAi
from apps.common.utils import join_values
from apps.core.models.prompt import Prompt
from apps.owasp.models.common import GenericEntityModel, RepositoryBasedEntityModel
from apps.owasp.models.managers.chapter import ActiveChaptertManager
from apps.owasp.models.mixins.chapter import ChapterIndexMixin


class Chapter(
    BulkSaveModel,
    ChapterIndexMixin,
    GenericEntityModel,
    RepositoryBasedEntityModel,
    TimestampedModel,
):
    """Chapter model."""

    objects = models.Manager()
    active_chapters = ActiveChaptertManager()

    class Meta:
        db_table = "owasp_chapters"
        verbose_name_plural = "Chapters"

    level = models.CharField(verbose_name="Level", max_length=5, default="", blank=True)

    country = models.CharField(verbose_name="Country", max_length=50, default="")
    region = models.CharField(verbose_name="Region", max_length=50, default="")
    postal_code = models.CharField(
        verbose_name="Postal code",
        max_length=15,
        default="",
        blank=True,
    )
    currency = models.CharField(verbose_name="Currency", max_length=10, default="", blank=True)
    meetup_group = models.CharField(
        verbose_name="Meetup group",
        max_length=100,
        default="",
        blank=True,
    )

    suggested_location = models.CharField(
        verbose_name="Suggested location",
        max_length=100,
        default="",
        blank=True,
    )  # AI suggested location.
    latitude = models.FloatField(verbose_name="Latitude", blank=True, null=True)
    longitude = models.FloatField(verbose_name="Longitude", blank=True, null=True)

    def __str__(self):
        """Chapter human readable representation."""
        return f"{self.name or self.key}"

    @staticmethod
    @lru_cache
    def active_chapters_count():
        """Return active chapters count."""
        return IndexBase.get_total_count("chapters")

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
        RepositoryBasedEntityModel.from_github(self, field_mapping, repository)

        if repository:
            self.created_at = repository.created_at
            self.updated_at = repository.updated_at

        # FKs.
        self.owasp_repository = repository

    def generate_geo_location(self):
        """Add latitude and longitude data."""
        location = None
        if self.suggested_location and self.suggested_location != "None":
            location = get_location_coordinates(self.suggested_location)
        if location is None:
            location = get_location_coordinates(self.get_geo_string())

        if location:
            self.latitude = location.latitude
            self.longitude = location.longitude

    def generate_suggested_location(self, open_ai=None, max_tokens=100):
        """Generate project summary."""
        if not self.is_active:
            return

        if not (prompt := Prompt.get_owasp_chapter_suggested_location()):
            return

        open_ai = open_ai or OpenAi()
        open_ai.set_input(self.get_geo_string())
        open_ai.set_max_tokens(max_tokens).set_prompt(prompt)
        suggested_location = open_ai.complete()
        self.suggested_location = (
            suggested_location if suggested_location and suggested_location != "None" else ""
        )

    def get_geo_string(self, include_name=True):
        """Return geo string."""
        return join_values(
            (
                self.name.replace("OWASP", "").strip() if include_name else "",
                self.country,
                self.postal_code,
            ),
            delimiter=", ",
        )

    def save(self, *args, **kwargs):
        """Save chapter."""
        if not self.suggested_location:
            self.generate_suggested_location()

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
