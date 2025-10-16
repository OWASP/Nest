"""Core app prompt model."""

import logging

from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify

from apps.common.models import TimestampedModel

logger: logging.Logger = logging.getLogger(__name__)


class Prompt(TimestampedModel):
    """Prompt model."""

    class Meta:
        db_table = "nest_prompts"
        verbose_name_plural = "Prompts"

    name = models.CharField(verbose_name="Name", max_length=100)
    key = models.CharField(verbose_name="Key", max_length=100, unique=True, blank=True)
    text = models.TextField(verbose_name="Text", max_length=2000, default="", blank=True)

    def __str__(self):
        """Prompt human readable representation."""
        return self.name

    def save(self, *args, **kwargs) -> None:
        """Save prompt."""
        self.key = slugify(self.name)

        super().save(*args, **kwargs)

    @staticmethod
    def get_text(key: str) -> str:
        """Return prompt by key.

        Args:
            key (str): The key of the prompt.

        Returns:
            str: The text of the prompt, or None if not found.

        """
        try:
            return Prompt.objects.get(key=key).text
        except Prompt.DoesNotExist:
            if settings.OPEN_AI_SECRET_KEY != "None":  # noqa: S105
                logger.warning("Prompt with key '%s' does not exist.", key)
            return ""

    @staticmethod
    def get_evaluator_system_prompt() -> str:
        """Return evaluator system prompt.

        Returns:
            str: The evaluator system prompt text.

        """
        return Prompt.get_text("evaluator-system-prompt")

    @staticmethod
    def get_github_issue_hint() -> str:
        """Return GitHub issue hint prompt.

        Returns
            str: The GitHub issue hint prompt text.

        """
        return Prompt.get_text("github-issue-hint")

    @staticmethod
    def get_github_issue_documentation_project_summary() -> str:
        """Return GitHub issue documentation project summary prompt.

        Returns
            str: The GitHub issue documentation project summary prompt text.

        """
        return Prompt.get_text("github-issue-documentation-project-summary")

    @staticmethod
    def get_github_issue_project_summary() -> str:
        """Return GitHub issue project summary prompt.

        Returns
            str: The GitHub issue project summary prompt text.

        """
        return Prompt.get_text("github-issue-project-summary")

    @staticmethod
    def get_metadata_extractor_prompt() -> str:
        """Return metadata extractor prompt.

        Returns
            str: The metadata extractor prompt text.

        """
        return Prompt.get_text("metadata-extractor-prompt")

    @staticmethod
    def get_owasp_chapter_suggested_location() -> str:
        """Return OWASP chapter suggested location prompt.

        Returns
            str: The OWASP chapter suggested location prompt text.

        """
        return Prompt.get_text("owasp-chapter-suggested-location")

    @staticmethod
    def get_owasp_chapter_summary() -> str:
        """Return OWASP chapter summary prompt.

        Returns
            str: The OWASP chapter summary prompt text.

        """
        return Prompt.get_text("owasp-chapter-summary")

    @staticmethod
    def get_owasp_committee_summary() -> str:
        """Return OWASP committee summary prompt.

        Returns
            str: The OWASP committee summary prompt text.

        """
        return Prompt.get_text("owasp-committee-summary")

    @staticmethod
    def get_owasp_event_suggested_location() -> str:
        """Return OWASP event suggested location prompt.

        Returns
            str: The OWASP event suggested location prompt text.

        """
        return Prompt.get_text("owasp-event-suggested-location")

    @staticmethod
    def get_owasp_event_summary() -> str:
        """Return OWASP event summary prompt.

        Returns
            str: The OWASP event summary prompt text.

        """
        return Prompt.get_text("owasp-event-summary")

    @staticmethod
    def get_owasp_project_summary() -> str:
        """Return OWASP project summary prompt.

        Returns
            str: The OWASP project summary prompt text.

        """
        return Prompt.get_text("owasp-project-summary")

    @staticmethod
    def get_rag_system_prompt() -> str:
        """Return RAG system prompt.

        Returns
            str: The RAG system prompt text.

        """
        return Prompt.get_text("rag-system-prompt")

    @staticmethod
    def get_slack_question_detector_prompt() -> str:
        """Return Slack question detector prompt.

        Returns
            str: The Slack question detector prompt text.

        """
        return Prompt.get_text("slack-question-detector-system-prompt")
