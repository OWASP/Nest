"""OWASP app common models."""

from __future__ import annotations

import itertools
import logging
import re
from urllib.parse import urlparse

import yaml
from django.db import models

from apps.common.open_ai import OpenAi
from apps.github.constants import (
    GITHUB_REPOSITORY_RE,
    GITHUB_USER_RE,
)
from apps.github.utils import get_repository_file_content

logger = logging.getLogger(__name__)


class RepositoryBasedEntityModel(models.Model):
    """Repository based entity model."""

    class Meta:
        abstract = True

    name = models.CharField(verbose_name="Name", max_length=100)
    key = models.CharField(verbose_name="Key", max_length=100, unique=True)
    description = models.CharField(
        verbose_name="Description", max_length=500, blank=True, default=""
    )
    summary = models.TextField(
        verbose_name="Summary", default="", blank=True
    )  # AI generated summary

    has_active_repositories = models.BooleanField(
        verbose_name="Has active repositories", default=True
    )
    is_active = models.BooleanField(verbose_name="Is active", default=True)

    tags = models.JSONField(verbose_name="OWASP metadata tags", default=list)
    topics = models.JSONField(
        verbose_name="GitHub repository topics", default=list, blank=True, null=True
    )

    created_at = models.DateTimeField(verbose_name="Created at", blank=True, null=True)
    updated_at = models.DateTimeField(verbose_name="Updated at", blank=True, null=True)

    leaders_raw = models.JSONField(
        verbose_name="Entity leaders list", default=list, blank=True, null=True
    )
    related_urls = models.JSONField(
        verbose_name="Entity related URLs", default=list, blank=True, null=True
    )
    invalid_urls = models.JSONField(
        verbose_name="Entity invalid related URLs", default=list, blank=True, null=True
    )
    is_leaders_policy_compliant = models.BooleanField(
        verbose_name="Is leaders policy compliant", default=True
    )

    # FKs.
    owasp_repository = models.ForeignKey(
        "github.Repository",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
    )

    # M2Ms.
    leaders = models.ManyToManyField(
        "github.User",
        verbose_name="Leaders",
        related_name="assigned_%(class)s",
        blank=True,
    )
    suggested_leaders = models.ManyToManyField(
        "github.User",
        verbose_name="Suggested leaders",
        related_name="matched_%(class)s",
        blank=True,
    )

    @property
    def github_url(self) -> str:
        """Get GitHub URL."""
        return f"https://github.com/owasp/{self.key}"

    @property
    def index_md_url(self) -> str | None:
        """Return project's raw index.md GitHub URL."""
        return (
            "https://raw.githubusercontent.com/OWASP/"
            f"{self.owasp_repository.key}/{self.owasp_repository.default_branch}/index.md"
            if self.owasp_repository
            else None
        )

    @property
    def leaders_md_url(self) -> str | None:
        """Return entity's raw leaders.md GitHub URL."""
        return (
            "https://raw.githubusercontent.com/OWASP/"
            f"{self.owasp_repository.key}/{self.owasp_repository.default_branch}/leaders.md"
            if self.owasp_repository
            else None
        )

    @property
    def owasp_name(self) -> str:
        """Get OWASP name."""
        return self.name if self.name.startswith("OWASP ") else f"OWASP {self.name}"

    @property
    def owasp_url(self) -> str:
        """Get OWASP URL."""
        return f"https://owasp.org/{self.key}"

    def deactivate(self):
        """Deactivate entity."""
        self.is_active = False
        self.save(update_fields=("is_active",))

    def from_github(self, field_mapping):
        """Update instance based on GitHub repository data."""
        entity_metadata = self.get_metadata()
        for model_field, gh_field in field_mapping.items():
            value = entity_metadata.get(gh_field)
            if value:
                setattr(self, model_field, value)

        self.leaders_raw = self.get_leaders()
        self.is_leaders_policy_compliant = len(self.leaders_raw) > 1

        self.tags = self.parse_tags(entity_metadata.get("tags", None) or [])

        return entity_metadata

    def generate_summary(self, prompt, open_ai=None, max_tokens=500):
        """Generate entity summary."""
        if not prompt:
            return

        open_ai = open_ai or OpenAi()
        open_ai.set_input(get_repository_file_content(self.index_md_url))
        open_ai.set_max_tokens(max_tokens).set_prompt(prompt)
        self.summary = open_ai.complete() or ""

    def get_leaders(self):
        """Get leaders from leaders.md file on GitHub."""
        content = get_repository_file_content(self.leaders_md_url)
        if not content:
            return []

        leaders = []
        for line in content.split("\n"):
            leaders.extend(
                [
                    name
                    for name in itertools.chain(
                        *re.findall(
                            r"[-*]\s*\[\s*([^(]+?)\s*(?:\([^)]*\))?\]|\*\s*([\w\s]+)", line.strip()
                        )
                    )
                    if name.strip()
                ]
            )

        return leaders

    def get_metadata(self):
        """Get entity metadata."""
        try:
            yaml_content = re.search(
                r"^---\s*([\s\S]*?)\s*---",
                get_repository_file_content(self.index_md_url),
                re.DOTALL,
            )
            return yaml.safe_load(yaml_content.group(1)) or {} if yaml_content else {}
        except (AttributeError, yaml.scanner.ScannerError):
            logger.exception(
                "Unable to parse entity metadata",
                extra={"repository": getattr(self.owasp_repository, "name", None)},
            )

    def get_related_url(self, url, exclude_domains=(), include_domains=()) -> str | None:
        """Get OWASP entity related URL."""
        if (
            not url
            or url.startswith("/cdn-cgi/l/email-protection")
            or any(urlparse(url).netloc == domain for domain in exclude_domains)
        ):
            return None

        if include_domains and not any(
            urlparse(url).netloc == domain for domain in include_domains
        ):
            return None

        if match := GITHUB_REPOSITORY_RE.match(url):
            return f"https://github.com/{match.group(1)}/{match.group(2)}".lower()

        if match := GITHUB_USER_RE.match(url):
            return f"https://github.com/{match.group(1)}".lower()

        return url

    def parse_tags(self, tags) -> list[str]:
        """Parse entity tags."""
        if not tags:
            return []

        return (
            [tag.strip(", ") for tag in tags.split("," if "," in tags else " ")]
            if isinstance(tags, str)
            else tags
        )
