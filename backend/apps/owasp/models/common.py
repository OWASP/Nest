"""OWASP app common models."""

from __future__ import annotations

import logging
import re
from functools import cached_property
from urllib.parse import urlparse

import yaml
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.common.models import BulkSaveModel
from apps.common.open_ai import OpenAi
from apps.common.utils import clean_url, validate_url
from apps.github.constants import (
    GITHUB_REPOSITORY_RE,
    GITHUB_USER_RE,
)
from apps.github.utils import get_repository_file_content
from apps.owasp.models.entity_channel import EntityChannel
from apps.owasp.models.entity_member import EntityMember
from apps.owasp.models.enums.project import AudienceChoices

logger = logging.getLogger(__name__)


class RepositoryBasedEntityModel(models.Model):
    """Repository based entity model."""

    class Meta:
        """Model options."""

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

    # GRs.
    entity_members = GenericRelation(
        EntityMember,
        content_type_field="entity_type",
        object_id_field="entity_id",
        related_query_name="entity_member",
    )

    entity_channels = GenericRelation(
        EntityChannel,
        content_type_field="entity_type",
        object_id_field="entity_id",
        related_query_name="entity_channel",
    )

    @cached_property
    def entity_leaders(self) -> list[EntityMember]:
        """Return entity's leaders."""
        return self.entity_members.filter(role=EntityMember.Role.LEADER).order_by("order")

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
    def info_md_url(self) -> str | None:
        """Return entity's raw info.md GitHub URL."""
        return (
            "https://raw.githubusercontent.com/OWASP/"
            f"{self.owasp_repository.key}/{self.owasp_repository.default_branch}/info.md"
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

    def get_audience(self):
        """Get audience from info.md file on GitHub."""
        content = get_repository_file_content(self.info_md_url)
        if not content:
            return []

        found_keywords = set()

        for line in content.split("\n"):
            for lower_kw, original_kw in AudienceChoices.choices:
                if original_kw in line:
                    found_keywords.add(lower_kw)

        return sorted(found_keywords)

    def get_leaders(self):
        """Get leaders from leaders.md file on GitHub."""
        content = get_repository_file_content(self.leaders_md_url)
        if not content:
            return []

        leaders = []
        # Compile regex patterns once per method call (before loop).
        re_bracketed_pattern = re.compile(
            r"[-*]\s{0,3}\[\s{0,3}([^\]\(]{1,200})(?:\s{0,3}\([^)]{0,100}\))?\s{0,3}\]"
        )
        re_plain_pattern = re.compile(r"\*\s{0,3}([\w\s]{1,200})")
        re_parenthetical_cleanup_pattern = re.compile(r"\s{0,3}\([^)]{0,100}\)\s{0,3}$")
        for line in content.split("\n"):
            stripped_line = line.strip()
            names = []

            names.extend(re_bracketed_pattern.findall(stripped_line))
            names.extend(re_plain_pattern.findall(stripped_line))

            cleaned_names = []
            for raw_name in names:
                if raw_name.strip():
                    cleaned = re_parenthetical_cleanup_pattern.sub("", raw_name).strip()
                    cleaned_names.append(cleaned)

            leaders.extend(cleaned_names)

        return leaders

    def get_leaders_emails(self):
        """Get leaders emails from leaders.md file on GitHub."""
        content = get_repository_file_content(self.leaders_md_url)
        if not content:
            return {}

        leaders = {}
        for line in content.split("\n"):
            matches = re.findall(
                r"^[-*]\s*\[([^\]]+)\]\((?:mailto:)?([^)]+)(\)|([^[<\n]))", line.strip()
            )

            for match in matches:
                if match[0] and match[1]:  # Name with email
                    leaders[match[0].strip()] = match[1].strip()
                elif match[2]:  # Name without email
                    leaders[match[2].strip()] = None

        return leaders

    def get_metadata(self):
        """Get entity metadata."""
        try:
            yaml_content = re.search(
                r"^---\s*(.*?)\s*---",
                get_repository_file_content(self.index_md_url),
                re.DOTALL,
            )
            return (
                yaml.safe_load(content)
                if yaml_content and (content := yaml_content.group(1))
                else {}
            )
        except (AttributeError, yaml.scanner.ScannerError):
            logger.exception(
                "Unable to parse entity metadata",
                extra={"repository": getattr(self.owasp_repository, "name", None)},
            )
            return {}

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

    def get_urls(self, domain=None):
        """Get URLs from info.md file on GitHub."""
        content = get_repository_file_content(self.info_md_url)
        if not content:
            return []

        urls = set()

        markdown_links = re.findall(r"\[([^\]]*)\]\((https?://[^\s\)]+)\)", content)
        for _text, url in markdown_links:
            cleaned_url = clean_url(url)
            if cleaned_url and validate_url(cleaned_url):
                urls.add(cleaned_url)

        standalone_urls = re.findall(r"(?<!\]\()https?://[^\s\)]+", content)
        for url in standalone_urls:
            cleaned_url = clean_url(url)
            if cleaned_url and validate_url(cleaned_url):
                urls.add(cleaned_url)

        if domain:
            domain_urls = set()
            for url in urls:
                try:
                    if urlparse(url).netloc == domain:
                        domain_urls.add(url)
                except ValueError:
                    pass
            urls = domain_urls

        return sorted(urls)

    def parse_tags(self, tags) -> list[str]:
        """Parse entity tags."""
        if not tags:
            return []

        return (
            [tag.strip(", ") for tag in tags.split("," if "," in tags else " ")]
            if isinstance(tags, str)
            else tags
        )

    def sync_leaders(self, leaders_emails):
        """Sync Leaders data.

        Args:
            leaders_emails (dict[str, str | None]): A dictionary
            where keys are the full names of the leaders
            and values are their corresponding email addresses (or None if no email is provided).

        """
        content_type = ContentType.objects.get_for_model(self.__class__)

        leaders = []
        for order, (name, email) in enumerate(leaders_emails.items()):
            leaders.append(
                EntityMember.update_data(
                    {
                        "entity_id": self.id,
                        "entity_type": content_type,
                        "member_email": email or "",
                        "member_name": name,
                        "order": (order + 1) * 100,
                        "role": EntityMember.Role.LEADER,
                    },
                    save=False,
                )
            )

        if leaders:
            BulkSaveModel.bulk_save(EntityMember, leaders)
