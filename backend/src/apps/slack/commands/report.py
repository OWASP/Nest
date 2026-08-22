"""Slack bot report command."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from django.conf import settings

from apps.slack.commands.command import CommandBase
from apps.slack.enums import ReportSource
from apps.slack.models.message import Message
from apps.slack.models.workspace import Workspace
from apps.slack.utils.report_modal import (
    FEATURE_OFF_TEXT,
    INVALID_LINK_TEXT,
    NOT_VISIBLE_TEXT,
    USAGE_TEXT,
)
from apps.slack.utils.report_open import make_ephemeral, open_report_content_modal

if TYPE_CHECKING:
    from slack_sdk import WebClient

logger = logging.getLogger(__name__)


class Report(CommandBase):
    """Slack bot /report command."""

    def handler(self, ack, command: dict[str, Any], client: WebClient, respond=None) -> None:
        """Resolve a message permalink and open the shared report modal."""
        ack()

        if not settings.SLACK_COMMANDS_ENABLED:
            return

        response_url = command.get("response_url") or ""
        ephemeral = make_ephemeral(respond, response_url)

        reporter_user_id = command.get("user_id") or ""
        team_id = command.get("team_id")
        trigger_id = command.get("trigger_id") or ""
        text = (command.get("text") or "").strip()

        if not reporter_user_id or not team_id or not trigger_id:
            logger.warning("Ignoring incomplete /report command payload")
            return

        if not text:
            ephemeral(text=USAGE_TEXT)
            return

        parsed = Message.parse_permalink(text)
        if parsed is None:
            ephemeral(text=INVALID_LINK_TEXT)
            return

        channel_id, message_ts, thread_ts = parsed
        workspace = Workspace.get_by_workspace_id(team_id)
        if workspace is None or not workspace.is_content_reporting_enabled:
            ephemeral(text=FEATURE_OFF_TEXT)
            return

        message_payload = Message.load_payload(
            client,
            channel_id,
            message_ts,
            thread_ts,
        )
        if message_payload is None:
            ephemeral(text=NOT_VISIBLE_TEXT)
            return

        if not message_payload.get("ts"):
            message_payload = {**message_payload, "ts": message_ts}

        open_report_content_modal(
            client=client,
            workspace=workspace,
            channel_id=channel_id,
            message_payload=message_payload,
            reporter_user_id=reporter_user_id,
            response_url=response_url,
            trigger_id=trigger_id,
            source=str(ReportSource.COMMAND),
            respond=respond,
        )
