"""Check OWASP Slack invite usage vs baseline and alert maintainers when needed."""

from __future__ import annotations

import logging

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from github.GithubException import GithubException
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from apps.github.auth import get_github_client
from apps.github.constants import OWASP_GITHUB_IO, OWASP_LOGIN
from apps.github.utils import get_latest_invite_link_commit
from apps.slack.models import Workspace

logger = logging.getLogger(__name__)

ERR_NO_DEFAULT_WORKSPACE = "Default OWASP Slack workspace is not configured in the database."
ERR_INVITE_BASELINE_UNSET = "invite_link_member_count is unset; cannot evaluate alerts."

MSG_SKIP_NO_ALERT_CHANNEL = (
    "invite_link_alert_channel_id is not set; skipping invite link checks "
    "(GitHub sync and threshold alerts). Set it on the Slack Workspace row when you want "
    "this job enabled."
)


class Command(BaseCommand):
    help = (
        "Sync public invite metadata from GitHub, set baseline when a new invite commit "
        "is detected, and alert when member growth approaches the invite link cap. "
        "Uses Workspace.total_members_count from the last slack_sync_data run (users.list totals)."
    )

    @staticmethod
    def get_normalized_invite_link_alert_channel_id(workspace: Workspace) -> str:
        """Return normalized alert channel id."""
        return (workspace.invite_link_alert_channel_id or "").strip().removeprefix("#")

    def alert(self, workspace: Workspace, current_members: int) -> None:
        alert_threshold = workspace.invite_link_alert_threshold
        if alert_threshold is None:
            raise CommandError(ERR_INVITE_BASELINE_UNSET)

        if current_members < alert_threshold:
            self.stdout.write(f"OK: current={current_members}, threshold={alert_threshold}.")
            return

        if workspace.invite_link_last_alert_sent_at is not None:
            self.stdout.write(
                self.style.WARNING(
                    "Threshold already reached; alert was sent earlier. "
                    "Set a new baseline in Django admin after publishing a new invite link."
                )
            )
            return

        baseline = workspace.invite_link_member_count
        created = workspace.invite_link_created_at
        sha = (workspace.invite_link_commit_sha or "").strip()
        commit_url = f"https://github.com/{OWASP_LOGIN}/{OWASP_GITHUB_IO}/commit/{sha}"
        link_label = created.date().isoformat() if created else sha[:7]
        last_updated = f"<{commit_url}|{link_label}>"

        body = (
            "*🚨 OWASP Slack invite link is approaching its usage limit.*\n\n"
            f"Current members: {current_members}\n"
            f"Baseline when link was set: {baseline}\n"
            f"Alert threshold: {workspace.invite_link_alert_threshold}\n"
            f"Public invite last updated: {last_updated}\n\n"
            "*Please generate a new invite link and update the site before the "
            "current link expires.*"
        )
        cc_line = self.invite_link_alert_cc_line(workspace.invite_link_alert_user_ids)
        text = f"{body}{cc_line}"

        try:
            client = WebClient(token=workspace.bot_token)
            client.chat_postMessage(
                channel=self.get_normalized_invite_link_alert_channel_id(workspace),
                text=text,
            )
        except SlackApiError as e:
            logger.exception("chat.postMessage failed")
            detail = e.response.get("error", e)
            msg = f"Slack chat.postMessage error: {detail}"
            raise CommandError(msg) from e

        workspace.invite_link_last_alert_sent_at = timezone.now()
        workspace.save(update_fields=["invite_link_last_alert_sent_at"])
        self.stdout.write(self.style.SUCCESS("Alert posted to Slack."))

    def handle(self, *args, **_options):
        workspace = Workspace.get_default_workspace()
        if workspace is None:
            raise CommandError(ERR_NO_DEFAULT_WORKSPACE)

        if not self.get_normalized_invite_link_alert_channel_id(workspace):
            self.stdout.write(self.style.WARNING(MSG_SKIP_NO_ALERT_CHANNEL))
            return

        if not workspace.bot_token:
            wid = workspace.slack_workspace_id.upper()
            msg = f"No SLACK_BOT_TOKEN_{wid} set for this workspace."
            raise CommandError(msg)

        invite_link_updated = self.sync_invite_created_at_from_github(workspace)

        workspace.refresh_from_db()
        current_members = workspace.total_members_count

        if workspace.invite_link_member_count is None and (
            invite_link_updated or workspace.invite_link_created_at is not None
        ):
            self.set_baseline(workspace, current_members)
            workspace.refresh_from_db()

        if workspace.invite_link_member_count is None:
            self.stdout.write(
                self.style.WARNING(
                    "Invite baseline not set; skipping threshold check. "
                    "Baseline is applied when a new invite-link commit is found on GitHub. "
                    "If you published a new link, ensure the commit message matches, or set "
                    "invite metadata and baseline in Django admin (after slack_sync_data for "
                    "current member counts)."
                )
            )
            return

        self.alert(workspace, current_members)

    def invite_link_alert_cc_line(self, user_ids: object) -> str:
        """Trailing ``cc:`` line with Slack ``<@user_id>`` mentions, or empty."""
        if not user_ids or not isinstance(user_ids, list):
            return ""
        parts = [f"<@{uid}>" for uid in user_ids if uid]
        if not parts:
            return ""
        return f"\n\ncc: {' '.join(parts)}"

    def set_baseline(self, workspace: Workspace, current_members: int) -> None:
        offset = (
            workspace.invite_link_alert_member_offset
            if workspace.invite_link_alert_member_offset is not None
            else 350
        )
        threshold = current_members + offset
        workspace.invite_link_member_count = current_members
        workspace.invite_link_last_alert_sent_at = None
        workspace.save(
            update_fields=[
                "invite_link_member_count",
                "invite_link_last_alert_sent_at",
            ]
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Baseline set: members={current_members}, alert at member count {threshold} "
                f"(baseline + offset {offset})."
            )
        )

    def sync_invite_created_at_from_github(self, workspace: Workspace) -> bool:
        """Sync invite commit time from GitHub.

        Returns:
            True if ``invite_link_created_at`` was written this run (new or refreshed link).

        """
        try:
            github = get_github_client()
            commit_date, commit_sha = get_latest_invite_link_commit(github)
        except GithubException as e:
            msg = f"GitHub API error: {e}"
            raise CommandError(msg) from e

        if commit_date is None:
            self.stdout.write(
                self.style.WARNING(
                    "No commit found with the expected message for _includes/slack_invite.html; "
                    "invite metadata not updated."
                )
            )
            return False

        commit_sha = (commit_sha or "").strip()
        stored_sha = (workspace.invite_link_commit_sha or "").strip()
        if workspace.invite_link_created_at == commit_date and stored_sha == commit_sha:
            self.stdout.write("Invite commit date and SHA already match GitHub.")
            return False

        workspace.invite_link_created_at = commit_date
        workspace.invite_link_commit_sha = commit_sha
        workspace.save(update_fields=["invite_link_created_at", "invite_link_commit_sha"])
        sha_note = f", sha={commit_sha[:7]}…" if commit_sha else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"invite_link_created_at set to {commit_date.isoformat()}{sha_note}"
            )
        )
        return True
