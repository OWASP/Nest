"""Github app repository model."""

from base64 import b64decode

import yaml
from django.db import models
from github.GithubException import GithubException

from apps.common.models import TimestampedModel
from apps.github.constants import OWASP_LOGIN
from apps.github.models.common import NodeModel
from apps.github.models.mixins import RepositoryIndexMixin
from apps.github.utils import (
    check_funding_policy_compliance,
    check_owasp_site_repository,
)

IGNORED_LANGUAGES = {"css", "html"}
LANGUAGE_PERCENTAGE_THRESHOLD = 1


class Repository(NodeModel, RepositoryIndexMixin, TimestampedModel):
    """Repository model."""

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("key", "owner"), name="unique_key_owner"),
        ]
        db_table = "github_repositories"
        verbose_name_plural = "Repositories"

    name = models.CharField(verbose_name="Name", max_length=100)
    key = models.CharField(verbose_name="Key", max_length=100)
    description = models.CharField(
        verbose_name="Description", max_length=1000, default="", blank=True
    )

    default_branch = models.CharField(verbose_name="Default branch", max_length=100, default="")
    homepage = models.CharField(verbose_name="Homepage", max_length=100, default="", blank=True)
    languages = models.JSONField(verbose_name="Languages", default=dict, blank=True)
    license = models.CharField(verbose_name="License", max_length=100, default="")
    size = models.PositiveIntegerField(verbose_name="Size in KB", default=0)
    topics = models.JSONField(verbose_name="Topics", default=list, blank=True)

    is_archived = models.BooleanField(verbose_name="Is archived", default=False)
    is_fork = models.BooleanField(verbose_name="Is fork", default=False)
    is_template = models.BooleanField(verbose_name="Is template", default=False)
    is_empty = models.BooleanField(verbose_name="Is empty", default=False)

    is_owasp_repository = models.BooleanField(verbose_name="Is OWASP repository", default=False)
    is_owasp_site_repository = models.BooleanField(
        verbose_name="Is OWASP site repository", default=False
    )

    is_funding_policy_compliant = models.BooleanField(
        verbose_name="Is funding policy compliant", default=True
    )
    has_funding_yml = models.BooleanField(verbose_name="Has FUNDING.yml", default=False)
    funding_yml = models.JSONField(verbose_name="FUNDING.yml data", default=dict, blank=True)
    pages_status = models.CharField(
        verbose_name="Pages status", max_length=20, default="", blank=True
    )

    has_downloads = models.BooleanField(verbose_name="Has downloads", default=False)
    has_issues = models.BooleanField(verbose_name="Has issues", default=False)
    has_pages = models.BooleanField(verbose_name="Has pages", default=False)
    has_projects = models.BooleanField(verbose_name="Has projects", default=False)
    has_wiki = models.BooleanField(verbose_name="Has wiki", default=False)

    commits_count = models.PositiveIntegerField(verbose_name="Commits", default=0)
    contributors_count = models.PositiveIntegerField(verbose_name="Contributors", default=0)
    forks_count = models.PositiveIntegerField(verbose_name="Forks", default=0)
    open_issues_count = models.PositiveIntegerField(verbose_name="Open issues", default=0)
    stars_count = models.PositiveIntegerField(verbose_name="Stars", default=0)
    subscribers_count = models.PositiveIntegerField(verbose_name="Subscribers", default=0)
    watchers_count = models.PositiveIntegerField(verbose_name="Watchers", default=0)

    created_at = models.DateTimeField(verbose_name="Created at")
    updated_at = models.DateTimeField(verbose_name="Updated at")
    pushed_at = models.DateTimeField(verbose_name="Pushed at")

    track_issues = models.BooleanField(verbose_name="Track issues", default=True)

    # FKs.
    organization = models.ForeignKey(
        "github.Organization",
        verbose_name="Organization",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    owner = models.ForeignKey(
        "github.User",
        verbose_name="Owner",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        """Repository human readable representation."""
        return self.path

    @property
    def is_indexable(self):
        """Repositories to index."""
        return (
            not self.is_archived
            and not self.is_empty
            and not self.is_template
            and self.project_set.exists()
        )

    @property
    def latest_release(self):
        """Repository latest release."""
        return self.published_releases.order_by("-published_at").first()

    @property
    def nest_key(self):
        """Return repository Nest key."""
        return f"{self.owner.login}-{self.name}"

    @property
    def path(self):
        """Return repository path."""
        return f"{self.owner.login}/{self.name}"

    @property
    def project(self):
        """Return project."""
        return self.project_set.first()

    @property
    def published_releases(self):
        """Return published releases."""
        return self.releases.filter(is_draft=False, published_at__isnull=False)

    @property
    def top_languages(self):
        """Return a list of top used languages."""
        return sorted(
            k
            for k, v in sorted(self.languages.items(), key=lambda pair: pair[1], reverse=True)
            if v >= LANGUAGE_PERCENTAGE_THRESHOLD and k.lower() not in IGNORED_LANGUAGES
        )

    def from_github(
        self,
        gh_repository,
        commits=None,
        contributors=None,
        languages=None,
        organization=None,
        user=None,
    ):
        """Update instance based on GitHub repository data."""
        field_mapping = {
            "created_at": "created_at",
            "default_branch": "default_branch",
            "description": "description",
            "forks_count": "forks_count",
            "has_downloads": "has_downloads",
            "has_issues": "has_issues",
            "has_pages": "has_pages",
            "has_projects": "has_projects",
            "has_wiki": "has_wiki",
            "homepage": "homepage",
            "is_archived": "archived",
            "is_fork": "fork",
            "is_template": "is_template",
            "name": "name",
            "open_issues_count": "open_issues_count",
            "pushed_at": "pushed_at",
            "size": "size",
            "stars_count": "stargazers_count",
            "subscribers_count": "subscribers_count",
            "topics": "topics",
            "updated_at": "updated_at",
            "watchers_count": "watchers_count",
        }

        # Direct fields.
        for model_field, gh_field in field_mapping.items():
            value = getattr(gh_repository, gh_field)
            if value is not None:
                setattr(self, model_field, value)

        # Key and OWASP repository flags.
        self.key = self.name.lower()
        self.is_owasp_repository = (
            organization is not None and organization.login.lower() == OWASP_LOGIN
        )
        self.is_owasp_site_repository = check_owasp_site_repository(self.key)

        # Commits.
        if commits is not None:
            try:
                self.commits_count = commits.totalCount
            except GithubException as e:
                if e.data["status"] == "409" and "Git Repository is empty" in e.data["message"]:
                    self.is_empty = True

        # Contributors.
        if contributors is not None:
            self.contributors_count = contributors.totalCount

        # Languages.
        if languages is not None:
            total_size = sum(languages.values())
            self.languages = {
                language: round(size * 100.0 / total_size, 1)
                for language, size in languages.items()
            }

        # License.
        self.license = gh_repository.license.spdx_id if gh_repository.license else ""

        # Fetch project metadata from funding.yml file.
        try:
            funding_yml = gh_repository.get_contents(".github/FUNDING.yml")
            yaml_content = b64decode(funding_yml.content).decode()
            self.funding_yml = yaml.safe_load(yaml_content)
            self.has_funding_yml = True

            # Set funding policy compliance flag.
            is_funding_policy_compliant = True
            for platform, targets in self.funding_yml.items():
                for target in targets if isinstance(targets, list) else [targets]:
                    if not target:
                        continue
                    is_funding_policy_compliant = check_funding_policy_compliance(
                        platform,
                        target,
                    )

                    if not is_funding_policy_compliant:
                        break

                if not is_funding_policy_compliant:
                    break
            self.is_funding_policy_compliant = is_funding_policy_compliant
        except GithubException:
            self.has_funding_yml = False
            self.is_funding_policy_compliant = True

        # FKs.
        self.organization = organization
        self.owner = user

    @staticmethod
    def update_data(
        gh_repository,
        commits=None,
        contributors=None,
        languages=None,
        organization=None,
        user=None,
        save=True,
    ):
        """Update repository data."""
        repository_node_id = Repository.get_node_id(gh_repository)
        try:
            repository = Repository.objects.get(node_id=repository_node_id)
        except Repository.DoesNotExist:
            repository = Repository(node_id=repository_node_id)

        repository.from_github(
            gh_repository,
            commits=commits,
            contributors=contributors,
            languages=languages,
            organization=organization,
            user=user,
        )
        if save:
            repository.save()

        return repository
