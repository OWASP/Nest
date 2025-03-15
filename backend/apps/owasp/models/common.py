"""OWASP app common models."""

import logging
import re
from urllib.parse import urlparse

import yaml
from django.db import models
from django.db.models import Sum
from requests.exceptions import RequestException

from apps.common.open_ai import OpenAi
from apps.github.constants import (
    GITHUB_REPOSITORY_RE,
    GITHUB_USER_RE,
)
from apps.github.models.repository_contributor import (
    TOP_CONTRIBUTORS_LIMIT,
    RepositoryContributor,
)
from apps.github.utils import get_repository_file_content

logger = logging.getLogger(__name__)


class RepositoryBasedEntityModel(models.Model):
    """Repository based entity model."""

    class Meta:
        abstract = True

    name = models.CharField(verbose_name="Name", max_length=100)
    key = models.CharField(verbose_name="Key", max_length=100, unique=True)
    description = models.CharField(verbose_name="Description", max_length=500, default="")
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

    # FKs.
    owasp_repository = models.ForeignKey(
        "github.Repository",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
    )

    @property
    def github_url(self):
        """Get GitHub URL."""
        return f"https://github.com/owasp/{self.key}"

    @property
    def leaders_md_raw_url(self):
        """Return entity's raw leaders.md GitHub URL."""
        return (
            "https://raw.githubusercontent.com/OWASP/"
            f"{self.owasp_repository.key}/{self.owasp_repository.default_branch}/leaders.md"
            if self.owasp_repository
            else None
        )

    @property
    def owasp_name(self):
        """Get OWASP name."""
        return self.name if self.name.startswith("OWASP ") else f"OWASP {self.name}"

    @property
    def owasp_url(self):
        """Get OWASP URL."""
        return f"https://owasp.org/{self.key}"

    def deactivate(self):
        """Deactivate entity."""
        self.is_active = False
        self.save(update_fields=("is_active",))

    def from_github(self, field_mapping, repository):
        """Update instance based on GitHub repository data."""
        # Get leaders.
        self.leaders_raw = self.get_leaders()

        # Normalize tags.
        self.tags = (
            [tag.strip(", ") for tag in self.tags.split("," if "," in self.tags else " ")]
            if isinstance(self.tags, str)
            else self.tags
        )

        project_metadata = {}

        index_md_content = get_repository_file_content(
            self.get_index_md_raw_url(repository=repository)
        )
        # Fetch project metadata from index.md file.
        try:
            yaml_content = re.search(r"^---\s*(.*?)\s*---", index_md_content, re.DOTALL)
            project_metadata = yaml.safe_load(yaml_content.group(1)) or {} if yaml_content else {}

            # Direct fields.
            for model_field, gh_field in field_mapping.items():
                value = project_metadata.get(gh_field)
                if value:
                    setattr(self, model_field, value)
        except (AttributeError, yaml.scanner.ScannerError):
            logger.exception("Unable to parse metadata", extra={"repository": repository.name})

        return project_metadata

    def generate_summary(self, prompt, open_ai=None, max_tokens=500):
        """Generate entity summary."""
        if not prompt:
            return

        open_ai = open_ai or OpenAi()
        open_ai.set_input(get_repository_file_content(self.get_index_md_raw_url()))
        open_ai.set_max_tokens(max_tokens).set_prompt(prompt)
        self.summary = open_ai.complete() or ""

    def get_index_md_raw_url(self, repository=None):
        """Return project's raw index.md GitHub URL."""
        owasp_repository = repository or self.owasp_repository
        return (
            "https://raw.githubusercontent.com/OWASP/"
            f"{owasp_repository.key}/{owasp_repository.default_branch}/index.md"
            if owasp_repository
            else None
        )

    def get_leaders(self):
        """Get leaders from leaders.md file on GitHub."""
        leaders = []

        try:
            content = get_repository_file_content(self.leaders_md_raw_url)
        except (RequestException, ValueError) as e:
            logger.exception(
                "Failed to fetch leaders.md file",
                extra={"URL": self.leaders_md_raw_url, "error": str(e)},
            )
            return leaders

        if not content:
            return leaders

        try:
            for line in content.split("\n"):
                logger.debug("Processing line: %s", line)
                # Match both standard Markdown list items with links and variations.
                leaders.extend(re.findall(r"\*\s*\[([^\]]+)\](?:\([^)]*\))?", line))
        except AttributeError:
            logger.exception(
                "Unable to parse leaders.md content", extra={"URL": self.leaders_md_raw_url}
            )

        return sorted(leaders)

    def get_related_url(self, url, exclude_domains=(), include_domains=()):
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

    def get_top_contributors(self, repositories=()):
        """Get top contributors."""
        return [
            {
                "avatar_url": tc["user__avatar_url"],
                "contributions_count": tc["total_contributions"],
                "login": tc["user__login"],
                "name": tc["user__name"],
            }
            for tc in RepositoryContributor.objects.by_humans()
            .filter(repository__in=repositories)
            .values(
                "user__avatar_url",
                "user__login",
                "user__name",
            )
            .annotate(total_contributions=Sum("contributions_count"))
            .order_by("-total_contributions")[:TOP_CONTRIBUTORS_LIMIT]
        ]
