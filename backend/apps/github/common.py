"""GitHub app common module."""

from __future__ import annotations

import logging
from datetime import timedelta as td

from django.utils import timezone
from github.GithubException import UnknownObjectException

from apps.github.models.issue import Issue
from apps.github.models.label import Label
from apps.github.models.milestone import Milestone
from apps.github.models.organization import Organization
from apps.github.models.pull_request import PullRequest
from apps.github.models.release import Release
from apps.github.models.repository import Repository
from apps.github.models.repository_contributor import RepositoryContributor
from apps.github.models.user import User
from apps.github.utils import check_owasp_site_repository

logger: logging.Logger = logging.getLogger(__name__)


def sync_repository(
    gh_repository, organization=None, user=None
) -> tuple[Organization, Repository]:
    """Sync GitHub repository data.

    Args:
        gh_repository (github.Repository.Repository): The GitHub repository object.
        organization (Organization, optional): The organization instance.
        user (User, optional): The user instance.

    Returns:
        tuple: A tuple containing the updated organization and repository instances.

    """
    entity_key = gh_repository.name.lower()
    is_owasp_site_repository = check_owasp_site_repository(entity_key)

    # Setup organization and user
    organization = organization or (
        Organization.update_data(gh_repository.organization)
        if gh_repository.organization
        else None
    )
    user = user or User.update_data(gh_repository.owner)

    # Create repository
    repository = Repository.update_data(
        gh_repository,
        commits=gh_repository.get_commits(),
        contributors=gh_repository.get_contributors(),
        languages=None if is_owasp_site_repository else gh_repository.get_languages(),
        organization=organization,
        user=user,
    )

    # Process repository content if not archived
    if not repository.is_archived:
        repository.sync_milestones(gh_repository)
        repository.sync_issues(gh_repository)
        repository.sync_pull_requests(gh_repository)

    repository.sync_releases(gh_repository, is_owasp_site_repository)
    repository.sync_contributors(gh_repository)

    return organization, repository


def _sync_repository_milestones(gh_repository, repository):
    """Sync repository milestones."""
    until = (
        repository.latest_updated_milestone.updated_at
        if repository.latest_updated_milestone
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
            repository=repository,
        )

        milestone.labels.clear()
        for gh_milestone_label in gh_milestone.get_labels():
            try:
                milestone.labels.add(Label.update_data(gh_milestone_label))
            except UnknownObjectException:
                logger.exception("Couldn't get GitHub milestone label %s", milestone.url)


def _sync_repository_issues(gh_repository, repository):
    """Sync repository issues."""
    project_track_issues = repository.project.track_issues if repository.project else True

    if not (repository.track_issues and project_track_issues):
        logger.info("Skipping issues sync for %s", repository.name)
        return

    until = (
        repository.latest_updated_issue.updated_at
        if repository.latest_updated_issue
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
                repository=repository,
            )
            if gh_issue.milestone
            else None
        )

        issue = Issue.update_data(
            gh_issue,
            author=User.update_data(gh_issue.user),
            milestone=milestone,
            repository=repository,
        )

        _update_assignees_and_labels(issue, gh_issue.assignees, gh_issue.labels, "issue")


def _sync_repository_pull_requests(gh_repository, repository):
    """Sync repository pull requests."""
    until = (
        repository.latest_updated_pull_request.updated_at
        if repository.latest_updated_pull_request
        else timezone.now() - td(days=30)
    )

    for gh_pull_request in gh_repository.get_pulls(direction="desc", sort="updated", state="all"):
        if gh_pull_request.updated_at < until:
            break

        milestone = (
            Milestone.update_data(
                gh_pull_request.milestone,
                author=User.update_data(gh_pull_request.milestone.creator),
                repository=repository,
            )
            if gh_pull_request.milestone
            else None
        )

        pull_request = PullRequest.update_data(
            gh_pull_request,
            author=User.update_data(gh_pull_request.user),
            milestone=milestone,
            repository=repository,
        )

        _update_assignees_and_labels(
            pull_request, gh_pull_request.assignees, gh_pull_request.labels, "pull request"
        )


def _update_assignees_and_labels(item, gh_assignees, gh_labels, item_type):
    """Update assignees and labels for issues/pull requests."""
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


def _sync_repository_releases(gh_repository, repository, is_owasp_site_repository):
    """Sync repository releases."""
    releases = []
    if not is_owasp_site_repository:
        existing_release_node_ids = set(
            Release.objects.filter(repository=repository).values_list("node_id", flat=True)
            if repository.id
            else ()
        )
        for gh_release in gh_repository.get_releases():
            release_node_id = Release.get_node_id(gh_release)
            if release_node_id in existing_release_node_ids:
                break

            releases.append(
                Release.update_data(
                    gh_release, author=User.update_data(gh_release.author), repository=repository
                )
            )
    Release.bulk_save(releases)


def _sync_repository_contributors(gh_repository, repository):
    """Sync repository contributors."""
    RepositoryContributor.bulk_save(
        [
            RepositoryContributor.update_data(gh_contributor, repository=repository, user=user)
            for gh_contributor in gh_repository.get_contributors()
            if (user := User.update_data(gh_contributor))
        ]
    )
