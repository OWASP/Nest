"""Core app prompt model."""

import logging

from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify

from apps.common.models import TimestampedModel

logger = logging.getLogger(__name__)


class Prompt(TimestampedModel):
    """Prompt model."""

    class Meta:
        db_table = "nest_prompts"
        verbose_name_plural = "Prompts"

    name = models.CharField(verbose_name="Name", max_length=100)
    key = models.CharField(verbose_name="Key", max_length=100, unique=True, blank=True)
    text = models.TextField(verbose_name="Text", max_length=1000, default="", blank=True)

    def __str__(self):
        """Prompt human readable representation."""
        return self.name

    def save(self, *args, **kwargs):
        """Save prompt."""
        self.key = slugify(self.name)

        super().save(*args, **kwargs)

    @staticmethod
    def get_text(key):
        """Return prompt by key."""
        try:
            return Prompt.objects.get(key=key).text
        except Prompt.DoesNotExist:
            if settings.OPEN_AI_SECRET_KEY != "None":  # noqa: S105
                logger.exception("Prompt with key '%s' does not exist.", key)

    @staticmethod
    def get_github_issue_hint():
        """Return GitHub issue hint prompt."""
        return Prompt.get_text("github-issue-hint")

    @staticmethod
    def get_github_issue_documentation_project_summary():
        """Return GitHub issue documentation project summary prompt."""
        return Prompt.get_text("github-issue-documentation-project-summary")

    @staticmethod
    def get_github_issue_project_summary():
        """Return GitHub issue project summary prompt."""
        return Prompt.get_text("github-issue-project-summary")

    @staticmethod
    def get_owasp_chapter_suggested_location():
        """Return OWASP chapter suggested location prompt."""
        return Prompt.get_text("owasp-chapter-suggested-location")

    @staticmethod
    def get_owasp_chapter_summary():
        """Return OWASP chapter summary prompt."""
        return Prompt.get_text("owasp-chapter-summary")

    @staticmethod
    def get_owasp_committee_summary():
        """Return OWASP committee summary prompt."""
        return Prompt.get_text("owasp-committee-summary")

    @staticmethod
    def get_owasp_project_summary():
        """Return OWASP project summary prompt."""
        return Prompt.get_text("owasp-project-summary")
