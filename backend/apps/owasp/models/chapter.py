"""OWASP app chapter model."""

from __future__ import annotations

from functools import lru_cache

from django.db import models

from apps.common.geocoding import get_location_coordinates
from apps.common.models import BulkSaveModel, TimestampedModel
from apps.common.open_ai import OpenAi
from apps.common.utils import get_absolute_url, join_values
from apps.core.models.prompt import Prompt
from apps.owasp.models.common import RepositoryBasedEntityModel
from apps.owasp.models.managers.chapter import ActiveChapterManager
from apps.owasp.models.mixins.chapter import ChapterIndexMixin


class Chapter(
    BulkSaveModel,
    ChapterIndexMixin,
    RepositoryBasedEntityModel,
    TimestampedModel,
):
    """Chapter model."""

    objects = models.Manager()
    active_chapters = ActiveChapterManager()

    class Meta:
        db_table = "owasp_chapters"
        indexes = [
            models.Index(fields=["-created_at"], name="chapter_created_at_desc_idx"),
            models.Index(fields=["-updated_at"], name="chapter_updated_at_desc_idx"),
        ]
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

    contribution_data = models.JSONField(
        verbose_name="Contribution Data",
        default=dict,
        blank=True,
        help_text="Daily contribution counts (YYYY-MM-DD -> count mapping)",
    )
    contribution_stats = models.JSONField(
        verbose_name="Contribution Statistics",
        default=dict,
        blank=True,
        help_text="Detailed contribution breakdown (commits, issues, pull requests, releases)",
    )

    def __str__(self) -> str:
        """Chapter human readable representation."""
        return f"{self.name or self.key}"

    @property
    def nest_key(self):
        """Get Nest key."""
        return self.key.replace("www-chapter-", "")

    @property
    def nest_url(self) -> str:
        """Get Nest URL for chapter."""
        return get_absolute_url(f"chapters/{self.nest_key}")

    @staticmethod
    @lru_cache
    def active_chapters_count():
        """Return active chapters count."""
        return Chapter.objects.filter(
            is_active=True,
            latitude__isnull=False,
            longitude__isnull=False,
            owasp_repository__is_empty=False,
        ).count()

    def from_github(self, repository) -> None:
        """Update instance based on GitHub repository data.

        Args:
            repository (github.Repository): The GitHub repository instance.

        """
        self.owasp_repository = repository

        RepositoryBasedEntityModel.from_github(
            self,
            {
                "country": "country",
                "currency": "currency",
                "level": "level",
                "meetup_group": "meetup-group",
                "name": "title",
                "postal_code": "postal-code",
                "region": "region",
                "tags": "tags",
            },
        )

        self.created_at = repository.created_at
        self.updated_at = repository.updated_at

    def generate_geo_location(self) -> None:
        """Add latitude and longitude data based on suggested location or geo string."""
        location = None
        if self.suggested_location and self.suggested_location != "None":
            location = get_location_coordinates(self.suggested_location)
        if location is None:
            location = get_location_coordinates(self.get_geo_string())

        if location:
            self.latitude = location.latitude
            self.longitude = location.longitude

    def generate_suggested_location(
        self,
        open_ai: OpenAi | None = None,
        max_tokens: int = 100,
    ) -> None:
        """Generate a suggested location using OpenAI.

        Args:
            open_ai (OpenAi, optional): An instance of OpenAi.
            max_tokens (int, optional): Maximum tokens for the OpenAI prompt.

        """
        if not (prompt := Prompt.get_owasp_chapter_suggested_location()):
            return

        open_ai = open_ai or OpenAi()
        open_ai.set_input(self.get_geo_string())
        open_ai.set_max_tokens(max_tokens).set_prompt(prompt)
        suggested_location = open_ai.complete()
        self.suggested_location = (
            suggested_location if suggested_location and suggested_location != "None" else ""
        )

    def get_geo_string(self, *, include_name: bool = True) -> str:
        """Return a geo string for the chapter.

        Args:
            include_name (bool, optional): Whether to include the chapter name.

        Returns:
            str: The geo string.

        """
        return join_values(
            [
                self.name.replace("OWASP", "").strip() if include_name else "",
                self.country,
                self.postal_code,
            ],
            delimiter=", ",
        )

    def save(self, *args, **kwargs) -> None:
        """Save the chapter instance."""
        if not self.suggested_location:
            self.generate_suggested_location()

        if self.latitude is None or self.longitude is None:
            self.generate_geo_location()

        super().save(*args, **kwargs)

    @staticmethod
    def bulk_save(  # type: ignore[override]
        chapters: list[Chapter],
        fields: tuple[str, ...] | None = None,
    ) -> None:
        """Bulk save chapters.

        Args:
            chapters (list[Chapter]): List of Chapter instances to save.
            fields (list[str], optional): List of fields to update.

        """
        BulkSaveModel.bulk_save(Chapter, chapters, fields=fields)

    @staticmethod
    def update_data(gh_repository, repository, *, save: bool = True) -> Chapter:
        """Update chapter data from GitHub repository.

        Args:
            gh_repository (github.Repository): The GitHub repository instance.
            repository (github.Repository): The repository data to update from.
            save (bool, optional): Whether to save the instance.

        Returns:
            Chapter: The updated Chapter instance.

        """
        key = gh_repository.name.lower()
        try:
            chapter = Chapter.objects.get(key=key)
        except Chapter.DoesNotExist:
            chapter = Chapter(key=key)

        chapter.from_github(repository)
        if save:
            chapter.save()

        return chapter
