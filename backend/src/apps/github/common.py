"""GitHub app common module."""

from __future__ import annotations

import logging
from contextlib import contextmanager, suppress
from datetime import UTC
from datetime import timedelta as td
from http import HTTPStatus
from itertools import batched
from typing import TYPE_CHECKING

from django.db import DatabaseError, connection, transaction
from django.utils import timezone
from github.GithubException import GithubException, UnknownObjectException

if TYPE_CHECKING:
    from datetime import datetime

    from github import Github

from apps.github.constants import GITHUB_ITEMS_PER_PAGE
from apps.github.models.comment import Comment
from apps.github.models.commit import Commit
from apps.github.models.issue import Issue
from apps.github.models.label import Label
from apps.github.models.milestone import Milestone
from apps.github.models.organization import Organization
from apps.github.models.pull_request import PullRequest
from apps.github.models.release import Release
from apps.github.models.repository import Repository
from apps.github.models.repository_contribution_sync_state import RepositoryContributionSyncState
from apps.github.models.repository_contributor import RepositoryContributor
from apps.github.models.user import User
from apps.github.utils import check_owasp_site_repository

logger: logging.Logger = logging.getLogger(__name__)


@contextmanager
def _repository_commit_sync_lock(repository):
    """Serialize a repository's commit imports without a long database transaction."""
    key = f"nest:github:commit-sync:{repository.pk}"
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_try_advisory_lock(hashtextextended(%s, 0))", [key])
        acquired = cursor.fetchone()[0]
    if not acquired:
        message = "Commit synchronization is already running for this repository"
        raise RuntimeError(message)
    try:
        yield
    finally:
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_unlock(hashtextextended(%s, 0))", [key])


def _repository_commit_head(gh_repository, branch):
    """Confirm an empty repository rather than treating arbitrary API errors as empty."""
    try:
        return gh_repository.get_branch(branch).commit.sha
    except GithubException as error:
        if error.status not in (HTTPStatus.NOT_FOUND, HTTPStatus.CONFLICT):
            raise
        try:
            if gh_repository.get_commits().totalCount == 0:
                return ""
        except GithubException as commits_error:
            if (
                commits_error.status == HTTPStatus.CONFLICT
                and isinstance(commits_error.data, dict)
                and (commits_error.data.get("message") or "").rstrip(".")
                == "Git Repository is empty"
            ):
                return ""
            raise
        raise


def _save_repository_commits(gh_commits, repository, users):
    """Upsert one bounded batch, retaining known authors when GitHub cannot resolve them."""
    by_node_id = {Commit.get_node_id(commit): commit for commit in gh_commits}
    existing = Commit.objects.filter(node_id__in=by_node_id).in_bulk(field_name="node_id")
    commits = []
    for node_id, gh_commit in by_node_id.items():
        commit = existing.get(node_id) or Commit(node_id=node_id, repository=repository)
        if commit.repository_id != repository.pk:
            message = "GitHub commit identity belongs to a different repository"
            raise ValueError(message)
        commit.sha = gh_commit.sha
        commit.message = gh_commit.commit.message
        commit.created_at = gh_commit.commit.author.date
        for field in ("author", "committer"):
            gh_user = getattr(gh_commit, field)
            if gh_user is None:
                continue
            user_node_id = User.get_node_id(gh_user)
            if user_node_id not in users:
                users[user_node_id] = User.objects.filter(node_id=user_node_id).first()
                if users[user_node_id] is None:
                    try:
                        users[user_node_id] = User.update_data(gh_user)
                    except UnknownObjectException as error:
                        if error.status != HTTPStatus.NOT_FOUND:
                            raise
            if users[user_node_id] is not None:
                setattr(commit, field, users[user_node_id])
        commits.append(commit)
    with transaction.atomic():
        Commit.objects.bulk_create(
            commits,
            update_conflicts=True,
            unique_fields=["node_id"],
            update_fields=[
                "sha",
                "message",
                "created_at",
                "author",
                "committer",
                "nest_updated_at",
            ],
        )


def sync_repository_commits(
    gh_repository, repository, *, start_at: datetime | None = None, end_at: datetime | None = None
) -> None:
    """Backfill authored commits, advancing coverage only after the pinned history completes.

    The start bounds retained history, not traversal: an old commit can precede newer
    authored commits in Git history. Already reachable future-dated commits are retained
    so advancing the head cannot lose them; aggregation applies its upper date bound.
    Failed runs retain committed batches for safe retry.
    """
    end_at = end_at or timezone.now()
    start_at = start_at or end_at - td(days=365)
    if timezone.is_naive(start_at) or timezone.is_naive(end_at) or start_at > end_at:
        message = "Commit sync requires an ordered timezone-aware period"
        raise ValueError(message)
    start_at, end_at = start_at.astimezone(UTC), end_at.astimezone(UTC)
    with _repository_commit_sync_lock(repository):
        state, _ = RepositoryContributionSyncState.objects.get_or_create(
            repository=repository, contribution_type="commits"
        )
        state.last_attempt_at = end_at
        state.save(update_fields=("last_attempt_at", "nest_updated_at"))
        try:
            branch = gh_repository.default_branch or ""
            head = _repository_commit_head(gh_repository, branch)
            users = {}
            history = gh_repository.get_commits(sha=head) if head else ()
            for page in batched(history, GITHUB_ITEMS_PER_PAGE, strict=False):
                eligible = [commit for commit in page if commit.commit.author.date >= start_at]
                if eligible:
                    _save_repository_commits(eligible, repository, users)
            # A full backfill verifies exactly this window; do not infer older coverage.
            state.covered_from = start_at
            state.covered_until = end_at
            state.default_branch = branch
            state.last_head_sha = head
            state.last_error = ""
            state.save(
                update_fields=(
                    "covered_from",
                    "covered_until",
                    "default_branch",
                    "last_head_sha",
                    "last_error",
                    "nest_updated_at",
                )
            )
        except Exception as error:
            # Exception messages/response bodies can contain secrets; store only the type.
            state.last_error = f"Commit import failed: {type(error).__name__}"
            with suppress(DatabaseError):
                state.save(update_fields=("last_error", "nest_updated_at"))
            raise


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
    contribution_end = timezone.now()
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

    sync_repository_commits(gh_repository, repository, end_at=contribution_end)

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

        gh_comments = gh_issue.get_comments(since=since) if since else gh_issue.get_comments()

        comments = []
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
