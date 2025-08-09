"""Github app repository model."""

from __future__ import annotations

import logging
from base64 import b64decode
from datetime import timedelta as td

import yaml
from django.db import models
from django.utils import timezone
from github.GithubException import GithubException, UnknownObjectException

from apps.common.models import TimestampedModel
from apps.github.constants import OWASP_LOGIN
from apps.github.models.common import NodeModel
from apps.github.models.issue import Issue
from apps.github.models.label import Label
from apps.github.models.milestone import Milestone
from apps.github.models.mixins import RepositoryIndexMixin
from apps.github.models.pull_request import PullRequest
from apps.github.models.release import Release
from apps.github.models.repository_contributor import RepositoryContributor
from apps.github.models.user import User
from apps.github.utils import (
    check_funding_policy_compliance,
    check_owasp_site_repository,
)

logger = logging.getLogger(__name__)

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
        related_name="repositories",
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
        """Return a human-readable representation of the repository.

        Returns
            str: The repository path.

        """
        return self.path

    @property
    def latest_pull_request(self):
        """Get the latest pull request for the repository.

        Returns
            PullRequest: The most recently created pull request.

        """
        return self.pull_requests.order_by("-created_at").first()

    @property
    def latest_release(self):
        """Get the latest release for the repository.

        Returns
            Release: The most recently published release.

        """
        return self.published_releases.order_by("-published_at").first()

    @property
    def latest_updated_issue(self):
        """Repository latest updated issue."""
        return self.issues.order_by("-updated_at").first()

    @property
    def latest_updated_milestone(self):
        """Repository latest updated milestone (most recently modified)."""
        return self.milestones.order_by("-updated_at").first()

    @property
    def latest_updated_pull_request(self):
        """Repository latest updated pull request (most recently modified)."""
        return self.pull_requests.order_by("-updated_at").first()

    @property
    def nest_key(self) -> str:
        """Return repository Nest key."""
        return f"{self.owner.login}-{self.name}"

    @property
    def path(self) -> str:
        """Return repository path."""
        return f"{self.owner.login}/{self.name}"

    @property
    def project(self):
        """Return project."""
        return self.project_set.first()

    @property
    def published_releases(self):
        """Return published releases."""
        return self.releases.filter(
            is_draft=False,
            is_pre_release=False,
            published_at__isnull=False,
        )

    @property
    def recent_milestones(self):
        """Repository recent milestones."""
        return Milestone.objects.filter(
            repository=self,
        ).order_by("-created_at")

    @property
    def top_languages(self) -> list[str]:
        """Return a list of top used languages."""
        return sorted(
            k
            for k, v in sorted(self.languages.items(), key=lambda pair: pair[1], reverse=True)
            if v >= LANGUAGE_PERCENTAGE_THRESHOLD and k.lower() not in IGNORED_LANGUAGES
        )

    @property
    def url(self) -> str:
        """Return repository URL."""
        return f"https://github.com/{self.path}"

    def from_github(
        self,
        gh_repository,
        commits=None,
        contributors=None,
        languages=None,
        organization=None,
        user=None,
    ) -> None:
        """Update the repository instance based on GitHub repository data.

        Args:
            gh_repository (github.Repository.Repository): The GitHub repository object.
            commits (github.PaginatedList.PaginatedList, optional): List of commits.
            contributors (github.PaginatedList.PaginatedList, optional): List of contributors.
            languages (dict, optional): Dictionary of languages used in the repository.
            organization (Organization, optional): The organization instance.
            user (User, optional): The user instance.

        """
        # Direct field mapping
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
        for model_field, gh_field in field_mapping.items():
            value = getattr(gh_repository, gh_field)
            if value is not None:
                setattr(self, model_field, value)

        # Repository metadata
        self.key = self.name.lower()
        self.is_owasp_repository = (
            organization is not None and organization.login.lower() == OWASP_LOGIN
        )
        self.is_owasp_site_repository = check_owasp_site_repository(self.key)

        # Process optional data sources
        optional_data = [
            (commits, self._process_commits_data),
            (contributors, self._process_contributors_data),
            (languages, self._process_languages_data),
        ]
        for data, processor in optional_data:
            if data is not None:
                processor(data)

        # License
        self.license = gh_repository.license.spdx_id if gh_repository.license else ""

        # Funding metadata
        self._process_funding_data(gh_repository)

        # Foreign keys
        self.organization = organization
        self.owner = user

    def _process_commits_data(self, commits):
        """Process commits data."""
        try:
            self.commits_count = commits.totalCount
        except GithubException as e:
            if e.data["status"] == "409" and "Git Repository is empty" in e.data["message"]:
                self.is_empty = True

    def _process_contributors_data(self, contributors):
        """Process contributors data."""
        self.contributors_count = contributors.totalCount

    def _process_languages_data(self, languages):
        """Process languages data."""
        total_size = sum(languages.values())
        self.languages = {
            language: round(size * 100.0 / total_size, 1) for language, size in languages.items()
        }

    def _process_funding_data(self, gh_repository):
        """Process funding.yml data."""
        try:
            funding_yml = gh_repository.get_contents(".github/FUNDING.yml")
            yaml_content = b64decode(funding_yml.content).decode()
            self.funding_yml = yaml.safe_load(yaml_content)
            self.has_funding_yml = True

            # Check funding policy compliance
            self.is_funding_policy_compliant = self._check_all_funding_compliance()
        except (AttributeError, GithubException):
            self.has_funding_yml = False
            self.is_funding_policy_compliant = True

    def _check_all_funding_compliance(self) -> bool:
        """Check if all funding targets are policy compliant."""
        for platform, targets in self.funding_yml.items():
            if not check_funding_policy_compliance(platform, targets):
                return False
        return True

    @staticmethod
    def update_data(
        gh_repository,
        *,
        commits=None,
        contributors=None,
        languages=None,
        organization=None,
        save: bool = True,
        user=None,
    ) -> Repository:
        """Update repository data.

        Args:
            gh_repository (github.Repository.Repository): The GitHub repository object.
            commits (github.PaginatedList.PaginatedList, optional): List of commits.
            contributors (github.PaginatedList.PaginatedList, optional): List of contributors.
            languages (dict, optional): Dictionary of languages used in the repository.
            organization (Organization, optional): The organization instance.
            user (User, optional): The user instance.
            save (bool, optional): Whether to save the instance.

        Returns:
            Repository: The updated or created repository instance.

        """
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

    def sync_milestones(self, gh_repository):
        """Sync milestones from GitHub repository."""
        until = (
            self.latest_updated_milestone.updated_at
            if self.latest_updated_milestone
            else timezone.now() - td(days=30)
        )
        for gh_milestone in gh_repository.get_milestones(
            direction="desc", sort="updated", state="all"
        ):
            if gh_milestone.updated_at < until:
                break
            milestone = Milestone.update_data(
                gh_milestone,
                author=User.update_data(gh_milestone.creator),
                repository=self,
            )
            milestone.labels.clear()
            for gh_milestone_label in gh_milestone.get_labels():
                try:
                    milestone.labels.add(Label.update_data(gh_milestone_label))
                except UnknownObjectException:
                    logger.exception("Couldn't get GitHub milestone label %s", milestone.url)

    def sync_issues(self, gh_repository):
        """Sync issues from GitHub repository."""
        project_track_issues = self.project.track_issues if self.project else True
        if not (self.track_issues and project_track_issues):
            logger.info("Skipping issues sync for %s", self.name)
            return
        until = (
            self.latest_updated_issue.updated_at
            if self.latest_updated_issue
            else timezone.now() - td(days=30)
        )
        for gh_issue in gh_repository.get_issues(direction="desc", sort="updated", state="all"):
            if gh_issue.pull_request:
                continue
            if gh_issue.updated_at < until:
                break
            milestone = (
                Milestone.update_data(
                    gh_issue.milestone,
                    author=User.update_data(gh_issue.milestone.creator),
                    repository=self,
                )
                if gh_issue.milestone
                else None
            )
            issue = Issue.update_data(
                gh_issue,
                author=User.update_data(gh_issue.user),
                milestone=milestone,
                repository=self,
            )
            self._update_assignees_and_labels(issue, gh_issue.assignees, gh_issue.labels, "issue")

    def sync_pull_requests(self, gh_repository):
        """Sync pull requests from GitHub repository."""
        until = (
            self.latest_updated_pull_request.updated_at
            if self.latest_updated_pull_request
            else timezone.now() - td(days=30)
        )
        for gh_pull_request in gh_repository.get_pulls(
            direction="desc", sort="updated", state="all"
        ):
            if gh_pull_request.updated_at < until:
                break
            milestone = (
                Milestone.update_data(
                    gh_pull_request.milestone,
                    author=User.update_data(gh_pull_request.milestone.creator),
                    repository=self,
                )
                if gh_pull_request.milestone
                else None
            )
            pull_request = PullRequest.update_data(
                gh_pull_request,
                author=User.update_data(gh_pull_request.user),
                milestone=milestone,
                repository=self,
            )
            self._update_assignees_and_labels(
                pull_request, gh_pull_request.assignees, gh_pull_request.labels, "pull request"
            )

    def _update_assignees_and_labels(self, item, gh_assignees, gh_labels, item_type):
        item.assignees.clear()
        for gh_assignee in gh_assignees:
            assignee = User.update_data(gh_assignee)
            if assignee:
                item.assignees.add(assignee)
        item.labels.clear()
        for gh_label in gh_labels:
            try:
                item.labels.add(Label.update_data(gh_label))
            except UnknownObjectException:
                logger.exception("Couldn't get GitHub %s label %s", item_type, item.url)

    def sync_releases(self, gh_repository, is_owasp_site_repository):
        """Sync releases from GitHub repository."""
        releases = []
        if not is_owasp_site_repository:
            existing_release_node_ids = set(
                Release.objects.filter(repository=self).values_list("node_id", flat=True)
                if self.id
                else ()
            )
            for gh_release in gh_repository.get_releases():
                release_node_id = Release.get_node_id(gh_release)
                if release_node_id in existing_release_node_ids:
                    break
                releases.append(
                    Release.update_data(
                        gh_release, author=User.update_data(gh_release.author), repository=self
                    )
                )
        Release.bulk_save(releases)

    def sync_contributors(self, gh_repository):
        """Sync contributors from GitHub repository."""
        RepositoryContributor.bulk_save(
            [
                RepositoryContributor.update_data(gh_contributor, repository=self, user=user)
                for gh_contributor in gh_repository.get_contributors()
                if (user := User.update_data(gh_contributor))
            ]
        )
