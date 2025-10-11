"""GitHub App authentication module."""

import logging
import os
from pathlib import Path

from django.conf import settings
from github import Auth, Github
from github.GithubException import BadCredentialsException

from apps.github.constants import GITHUB_ITEMS_PER_PAGE

logger = logging.getLogger(__name__)


class GitHubAppAuth:
    """GitHub App authentication handler."""

    def __init__(self):
        """Initialize GitHub App authentication."""
        self.app_id = settings.GITHUB_APP_ID
        self.app_installation_id = settings.GITHUB_APP_INSTALLATION_ID
        self.private_key = self._load_private_key()

        self.pat_token = os.getenv("GITHUB_TOKEN")

        if not self._is_app_configured() and not self.pat_token:
            error_message = (
                "GitHub App configuration is incomplete. "
                "Please set GITHUB_APP_ID and GITHUB_APP_INSTALLATION_ID, "
                "ensure backend/.github.pem file exists, "
                "or provide GITHUB_TOKEN for PAT authentication."
            )
            raise ValueError(error_message)

    def _is_app_configured(self) -> bool:
        """Check if GitHub App is properly configured."""
        return all((self.app_id, self.private_key, self.app_installation_id))

    def _load_private_key(self):
        """Load the GitHub App private key from a local file."""
        try:
            with (Path(settings.BASE_DIR) / ".github.pem").open("r") as key_file:
                return key_file.read().strip()
        except (FileNotFoundError, PermissionError):
            return None

    def get_github_client(self, per_page: int | None = None) -> Github:
        """Get authenticated GitHub client.

        Args:
            per_page: Number of items per page for pagination.

        Returns:
            Authenticated GitHub client instance.

        Raises:
            BadCredentialsException: If authentication fails.

        """
        per_page = per_page or GITHUB_ITEMS_PER_PAGE

        if self._is_app_configured():
            logger.warning("Using GitHub App authentication")
            return Github(
                auth=Auth.AppInstallationAuth(
                    app_auth=Auth.AppAuth(
                        app_id=self.app_id,
                        private_key=self.private_key,
                    ),
                    installation_id=int(self.app_installation_id),
                ),
                per_page=per_page,
            )

        if self.pat_token:
            logger.warning("Using GitHub PAT token")
            return Github(self.pat_token, per_page=per_page)

        raise BadCredentialsException(401, "Invalid GitHub credentials", None)


def get_github_client(per_page: int | None = None) -> Github:
    """Get authenticated GitHub client.

    Args:
        per_page: Number of items per page for pagination.

    Returns:
        Authenticated GitHub client instance.

    """
    return GitHubAppAuth().get_github_client(per_page=per_page)
