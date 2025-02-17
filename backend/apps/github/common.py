"""GitHub app common module."""

import logging

from github.GithubException import GithubException, UnknownObjectException

from apps.github.models.issue import Issue
from apps.github.models.label import Label
from apps.github.models.organization import Organization
from apps.github.models.pull_request import PullRequest
from apps.github.models.release import Release
from apps.github.models.repository import Repository
from apps.github.models.repository_contributor import RepositoryContributor
from apps.github.models.user import User
from apps.github.utils import check_owasp_site_repository

logger = logging.getLogger(__name__)


def sync_repository(gh_repository, organization=None, user=None):
    """Sync GitHub repository data."""
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

    # GitHub repository issues.
    if (
        not repository.is_archived
        and repository.track_issues
        and repository.project
        and repository.project.track_issues
    ):
        # Sync open issues for the first run.
        kwargs = {
            "direction": "asc",
            "sort": "created",
            "state": "open",
        }
        latest_issue = repository.latest_issue
        if latest_issue:
            # Sync open/closed issues for subsequent runs.
            kwargs.update(
                {
                    "since": latest_issue.updated_at,
                    "state": "all",
                }
            )
        for gh_issue in gh_repository.get_issues(**kwargs):
            # Skip pull requests.
            if gh_issue.pull_request:
                continue

            author = (
                User.update_data(gh_issue.user)
                if gh_issue.user and gh_issue.user.type != "Bot"
                else None
            )
            issue = Issue.update_data(gh_issue, author=author, repository=repository)

            # Assignees.
            issue.assignees.clear()
            for gh_issue_assignee in gh_issue.assignees:
                issue.assignees.add(User.update_data(gh_issue_assignee))

            # Labels.
            issue.labels.clear()
            for gh_issue_label in gh_issue.labels:
                try:
                    issue.labels.add(Label.update_data(gh_issue_label))
                except UnknownObjectException:
                    logger.info("Couldn't get GitHub issue label %s", issue.url)
    # GitHub Pull Requests Part!
    else:
        logger.info("Skipping issues sync for %s", repository.name)
    if not repository.is_archived and repository.project:
        kwargs = {
            "direction": "asc",
            "sort": "created",
            "state": "open",
        }

        open_gh_pull_requests = list(gh_repository.get_pulls(**kwargs))
        open_pr_numbers = {gh_pull_request.number for gh_pull_request in open_gh_pull_requests}

        closed_prs = PullRequest.objects.filter(repository=repository, state="open").exclude(
            number__in=open_pr_numbers
        )

        for pr in closed_prs:
            pr.state = "closed"
            try:
                gh_closed_pr = gh_repository.get_pull(pr.number)
                pr.closed_at = gh_closed_pr.closed_at  # Correct closure time from GitHub
                pr.merged_at = gh_closed_pr.merged_at  # Correct merge time if merged
            except GithubException:
                logger.warning(
                    "Could not fetch closed PR details for %s, using updated_at instead.",
                    pr.number,
                )
                pr.closed_at = pr.closed_at or pr.updated_at  # Fallback if API fails

            pr.save()

        for gh_pull_request in open_gh_pull_requests:
            author = (
                User.update_data(gh_pull_request.user)
                if gh_pull_request.user and gh_pull_request.user.type != "Bot"
                else None
            )

            pull_request = PullRequest.update_data(
                gh_pull_request, author=author, repository=repository
            )

            pull_request.assignees.clear()
            for gh_pull_request_assignee in gh_pull_request.assignees:
                pull_request.assignees.add(User.update_data(gh_pull_request_assignee))

            pull_request.labels.clear()
            for gh_pull_request_label in gh_pull_request.labels:
                try:
                    pull_request.labels.add(Label.update_data(gh_pull_request_label))
                except UnknownObjectException:
                    logger.info("Couldn't get GitHub pull request label %s", pull_request.url)
    else:
        logger.info("Skipping pull request sync for %s", repository.name)

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

            author = (
                User.update_data(gh_release.author)
                if gh_release.author and gh_release.author.type != "Bot"
                else None
            )
            releases.append(Release.update_data(gh_release, author=author, repository=repository))
    Release.bulk_save(releases)

    # GitHub repository contributors.
    repository_contributors = []
    for gh_contributor in gh_repository.get_contributors():
        user = (
            User.update_data(gh_contributor)
            if gh_contributor and gh_contributor.type != "Bot"
            else None
        )
        if user:
            repository_contributors.append(
                RepositoryContributor.update_data(gh_contributor, repository=repository, user=user)
            )
    RepositoryContributor.bulk_save(repository_contributors)

    return organization, repository
