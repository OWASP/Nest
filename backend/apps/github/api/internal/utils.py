"""GitHub API utilities for issue operations."""

import logging
from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from github.GithubException import GithubException

from apps.github.auth import get_github_client

if TYPE_CHECKING:
    from apps.github.models.issue import Issue

logger = logging.getLogger(__name__)


def get_github_issue_object(issue: "Issue"):
    """Get GitHub issue object from a local Issue model."""
    if not issue.repository:
        raise ValidationError(message="Issue has no repository.")

    try:
        gh_client = get_github_client()
        gh_repository = gh_client.get_repo(issue.repository.path)
        return gh_repository.get_issue(number=issue.number)
    except GithubException as e:
        logger.exception(
            "Failed to get GitHub issue",
            extra={"issue_id": issue.id, "issue_number": issue.number, "error": str(e)},
        )
        raise ValidationError(message=f"Failed to get issue from GitHub: {e}") from e


def assign_issue_to_user(issue: "Issue", user_login: str) -> None:
    """Assign a GitHub issue to a user."""
    try:
        gh_issue = get_github_issue_object(issue)
        gh_issue.add_to_assignees(user_login)
        logger.info(
            "Successfully assigned issue to user",
            extra={"issue_id": issue.id, "issue_number": issue.number, "user_login": user_login},
        )
    except GithubException as e:
        logger.exception(
            "Failed to assign issue on GitHub",
            extra={
                "issue_id": issue.id,
                "issue_number": issue.number,
                "user_login": user_login,
                "error": str(e),
            },
        )
        raise ValidationError(message=f"Failed to assign issue on GitHub: {e}") from e


def unassign_issue_from_user(issue: "Issue", user_login: str) -> None:
    """Unassign a GitHub issue from a user."""
    try:
        gh_issue = get_github_issue_object(issue)
        gh_issue.remove_from_assignees(user_login)
        logger.info(
            "Successfully unassigned issue from user",
            extra={"issue_id": issue.id, "issue_number": issue.number, "user_login": user_login},
        )
    except GithubException as e:
        logger.exception(
            "Failed to unassign issue on GitHub",
            extra={
                "issue_id": issue.id,
                "issue_number": issue.number,
                "user_login": user_login,
                "error": str(e),
            },
        )
        raise ValidationError(message=f"Failed to unassign issue on GitHub: {e}") from e
