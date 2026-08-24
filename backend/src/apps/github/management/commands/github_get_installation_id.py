"""A command to get GitHub App installation ID."""

import logging
import os
import sys
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from github import Auth, GithubIntegration

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Get GitHub App installation ID for the configured app."

    def add_arguments(self, parser):
        """Add command-line arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument(
            "--app-id",
            type=int,
            help="GitHub App ID (overrides GITHUB_APP_ID environment variable)",
        )
        parser.add_argument(
            "--private-key-file",
            type=str,
            help="Path to private key file (overrides default backend/.github.pem)",
        )

    def handle(self, *args, **options):
        """Handle the command execution.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments containing command options.

        """
        # Get app ID from arguments or environment
        app_id = options.get("app_id") or os.getenv("GITHUB_APP_ID")
        if not app_id:
            self.stderr.write(
                self.style.ERROR(
                    "GitHub App ID is required. "
                    "Provide --app-id argument or set GITHUB_APP_ID environment variable."
                )
            )
            sys.exit(1)

        # Get private key from file
        private_key_file = (
            options.get("private_key_file") or Path(settings.BASE_DIR) / ".github.pem"
        )
        if not Path(private_key_file).exists():
            self.stderr.write(
                self.style.ERROR(
                    f"Private key file not found: {private_key_file}. "
                    "Please ensure the file exists and contains your GitHub App private key."
                )
            )
            sys.exit(1)

        try:
            with Path(private_key_file).open("r") as key_file:
                private_key = key_file.read().strip()
                if not private_key:
                    self.stderr.write(
                        self.style.ERROR(f"Private key file is empty: {private_key_file}")
                    )
                    sys.exit(1)
        except (FileNotFoundError, PermissionError) as e:
            self.stderr.write(self.style.ERROR(f"Failed to read private key file: {e}"))
            sys.exit(1)

        try:
            # Create GitHub App authentication
            app_auth = Auth.AppAuth(app_id=int(app_id), private_key=private_key)

            # Create GitHub Integration instance
            gi = GithubIntegration(auth=app_auth)

            # Get all installations
            installations = list(gi.get_installations())

            if not installations:
                self.stdout.write(
                    self.style.WARNING(f"No installations found for GitHub App ID: {app_id}")
                )
                return

            self.stdout.write(
                self.style.SUCCESS(
                    f"Found {len(installations)} installation(s) for GitHub App ID: {app_id}"
                )
            )

            for installation in installations:
                self.stdout.write(f"Installation ID: {installation.id}")
                if hasattr(installation, "account") and installation.account:
                    account_type = installation.account.type
                    account_name = getattr(installation.account, "login", "N/A")
                    self.stdout.write(f"  Account: {account_name} ({account_type})")
                self.stdout.write("")

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to get installations: {e}"))
            logger.exception("Error getting GitHub App installations")
            sys.exit(1)
