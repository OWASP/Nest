"""Core app prompt model."""

from django.db import models
from django.template.defaultfilters import slugify

from apps.common.models import TimestampedModel


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
    def get_github_issue_hint():
        """Return GitHub issue hint prompt."""
        return Prompt.objects.get(key="github-issue-hint").text

    @staticmethod
    def get_github_issue_documentation_project_summary():
        """Return GitHub issue documentation project summary prompt."""
        return Prompt.objects.get(key="github-issue-documentation-project-summary").text

    @staticmethod
    def get_github_issue_project_summary():
        """Return GitHub issue project summary prompt."""
        return Prompt.objects.get(key="github-issue-project-summary").text

    @staticmethod
    def get_owasp_chapter_suggested_location():
        """Return OWASP chapter suggested location prompt."""
        return Prompt.objects.get(key="owasp-chapter-suggested-location").text

    @staticmethod
    def get_owasp_chapter_summary():
        """Return OWASP chapter summary prompt."""
        return Prompt.objects.get(key="owasp-chapter-summary").text

    @staticmethod
    def get_owasp_project_summary():
        """Return OWASP project summary prompt."""
        return Prompt.objects.get(key="owasp-project-summary").text
