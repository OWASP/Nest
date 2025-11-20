"""GitHub app common module."""

from __future__ import annotations

import logging
from datetime import timedelta as td
from typing import TYPE_CHECKING

from django.utils import timezone
from github.GithubException import UnknownObjectException

if TYPE_CHECKING:
    from github import Github

from apps.github.models.comment import Comment
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

    # GitHub repository organization.
    if organization is None:
        gh_organization = gh_repository.organization
        if gh_organization is not None:
            organization = Organization.update_data(gh_organization)

    # GitHub repository owner.
    if user is None:
        user = User.update_data(gh_repository.owner)

    # GitHub repository.
    commits = gh_repository.get_commits()
    contributors = gh_repository.get_contributors()
    languages = None if is_owasp_site_repository else gh_repository.get_languages()

    repository = Repository.update_data(
        gh_repository,
        commits=commits,
        contributors=contributors,
        languages=languages,
        organization=organization,
        user=user,
    )

    if not repository.is_archived:
        # GitHub repository milestones.
        kwargs = {
            "direction": "desc",
            "sort": "updated",
            "state": "all",
        }

        until = (
            latest_updated_milestone.updated_at
            if (latest_updated_milestone := repository.latest_updated_milestone)
            else timezone.now() - td(days=30)
        )

        for gh_milestone in gh_repository.get_milestones(**kwargs):
            if gh_milestone.updated_at < until:
                break

            milestone = Milestone.update_data(
                gh_milestone,
                author=User.update_data(gh_milestone.creator),
                repository=repository,
            )

            # Labels.
            milestone.labels.clear()
            for gh_milestone_label in gh_milestone.get_labels():
                try:
                    milestone.labels.add(Label.update_data(gh_milestone_label))
                except UnknownObjectException:
                    logger.exception("Couldn't get GitHub milestone label %s", milestone.url)

        # GitHub repository issues.
        project_track_issues = repository.project.track_issues if repository.project else True
        month_ago = timezone.now() - td(days=30)

        if repository.track_issues and project_track_issues:
            kwargs = {
                "direction": "desc",
                "sort": "updated",
                "state": "all",
            }
            until = (
                latest_updated_issue.updated_at
                if (latest_updated_issue := repository.latest_updated_issue)
                else month_ago
            )
            for gh_issue in gh_repository.get_issues(**kwargs):
                if gh_issue.pull_request:  # Skip pull requests.
                    continue

                if gh_issue.updated_at < until:
                    break

                author = User.update_data(gh_issue.user)

                # Milestone
                milestone = None
                if gh_issue.milestone:
                    milestone = Milestone.update_data(
                        gh_issue.milestone,
                        author=User.update_data(gh_issue.milestone.creator),
                        repository=repository,
                    )
                issue = Issue.update_data(
                    gh_issue,
                    author=author,
                    milestone=milestone,
                    repository=repository,
                )

                # Assignees.
                issue.assignees.clear()
                for gh_issue_assignee in gh_issue.assignees:
                    if issue_assignee := User.update_data(gh_issue_assignee):
                        issue.assignees.add(issue_assignee)

                # Labels.
                issue.labels.clear()
                for gh_issue_label in gh_issue.labels:
                    try:
                        issue.labels.add(Label.update_data(gh_issue_label))
                    except UnknownObjectException:
                        logger.exception("Couldn't get GitHub issue label %s", issue.url)
        else:
            logger.info("Skipping issues sync for %s", repository.name)

        # GitHub repository pull requests.
        kwargs = {
            "direction": "desc",
            "sort": "updated",
            "state": "all",
        }
        until = (
            latest_updated_pull_request.updated_at
            if (latest_updated_pull_request := repository.latest_updated_pull_request)
            else month_ago
        )
        for gh_pull_request in gh_repository.get_pulls(**kwargs):
            if gh_pull_request.updated_at < until:
                break

            author = User.update_data(gh_pull_request.user)

            # Milestone
            milestone = None
            if gh_pull_request.milestone:
                milestone = Milestone.update_data(
                    gh_pull_request.milestone,
                    author=User.update_data(gh_pull_request.milestone.creator),
                    repository=repository,
                )
            pull_request = PullRequest.update_data(
                gh_pull_request,
                author=author,
                milestone=milestone,
                repository=repository,
            )

            # Assignees.
            pull_request.assignees.clear()
            for gh_pull_request_assignee in gh_pull_request.assignees:
                if pull_request_assignee := User.update_data(gh_pull_request_assignee):
                    pull_request.assignees.add(pull_request_assignee)

            # Labels.
            pull_request.labels.clear()
            for gh_pull_request_label in gh_pull_request.labels:
                try:
                    pull_request.labels.add(Label.update_data(gh_pull_request_label))
                except UnknownObjectException:
                    logger.exception("Couldn't get GitHub pull request label %s", pull_request.url)

    # GitHub repository releases.
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

            author = User.update_data(gh_release.author)
            releases.append(Release.update_data(gh_release, author=author, repository=repository))
    Release.bulk_save(releases)

    # GitHub repository contributors.
    RepositoryContributor.bulk_save(
        [
            RepositoryContributor.update_data(
                gh_contributor,
                repository=repository,
                user=user,
            )
            for gh_contributor in gh_repository.get_contributors()
            if (user := User.update_data(gh_contributor))
        ]
    )

    return organization, repository


def sync_issue_comments(gh_client: Github, issue: Issue):
    """Sync new comments for a mentorship program specific issue on-demand.

    Args:
        gh_client (Github): GitHub client.
        issue (Issue): The local database Issue object to sync comments for.

    """
    logger.info("Starting comment sync for issue #%s", issue.number)

    try:
        if not (repository := issue.repository):
            logger.warning("Issue #%s has no repository, skipping", issue.number)
            return

        logger.info("Fetching repository: %s", repository.path)

        gh_repository = gh_client.get_repo(repository.path)
        gh_issue = gh_repository.get_issue(number=issue.number)

        since = (
            (issue.latest_comment.updated_at or issue.latest_comment.created_at)
            if issue.latest_comment
            else getattr(issue, "updated_at", None)
        )

        comments = []

        gh_comments = gh_issue.get_comments(since=since) if since else gh_issue.get_comments()

        for gh_comment in gh_comments:
            author = User.update_data(gh_comment.user)
            if not author:
                logger.warning("Could not sync author for comment %s", gh_comment.id)
                continue

            comment = Comment.update_data(
                gh_comment,
                author=author,
                content_object=issue,
                save=False,
            )
            comments.append(comment)

        if comments:
            Comment.bulk_save(comments)

        logger.info(
            "%d comments synced for issue #%s",
            len(comments),
            issue.number,
        )

    except UnknownObjectException as e:
        logger.warning(
            "Could not access issue #%s. Error: %s",
            issue.number,
            e,
        )
    except Exception:
        logger.exception(
            "An unexpected error occurred during comment sync for issue #%s",
            issue.number,
        )
