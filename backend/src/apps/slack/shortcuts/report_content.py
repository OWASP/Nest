"""Slack message shortcut and shared content-report handlers."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from apps.slack.enums import ReportSource
from apps.slack.modals.report import (
    ALREADY_REPORTED_TEXT,
    CONSENT_BLOCK_ID,
    FEATURE_OFF_TEXT,
    METADATA_UNAVAILABLE_TEXT,
    MISSING_MESSAGE_TEXT,
    PRIVATE_CHANNEL_TEXT,
    REPORT_CONTENT_CALLBACK_ID,
    REPORT_CONTENT_VIEW_CALLBACK_ID,
    REPORT_TYPE_BLOCK_ID,
    SELF_REPORT_TEXT,
    SUBMIT_FAILED_TEXT,
    SUCCESS_TEXT,
    consent_given,
    decode_metadata,
    selected_report_type,
)
from apps.slack.models.content_report import ContentReport
from apps.slack.models.message import Message
from apps.slack.models.workspace import Workspace
from apps.slack.shortcuts.shortcut import ShortcutBase
from apps.slack.utils.report import (
    WORKSPACE_MISMATCH_TEXT,
    make_ephemeral,
    open_report_content_modal,
    post_ephemeral_url,
    resolve_conversation,
)

if TYPE_CHECKING:
    from slack_sdk import WebClient

logger = logging.getLogger(__name__)


def load_submission_context(
    body: dict[str, Any],
    client: WebClient,
    view: dict[str, Any],
) -> tuple[Workspace, Message, str, str, str] | None:
    """Validate submission and return workspace, message, reporter, response_url, source."""
    reporter_user_id = (body.get("user") or {}).get("id") or ""
    team_id = (body.get("team") or {}).get("id") or view.get("team_id")
    metadata = decode_metadata(view.get("private_metadata") or "")
    if metadata is None or not reporter_user_id or not team_id:
        logger.warning("Ignoring invalid report_content submission")
        return None

    message_db_id, response_url, source = metadata
    if (
        workspace := Workspace.get_by_workspace_id(team_id)
    ) is None or not workspace.is_content_reporting_enabled:
        post_ephemeral_url(response_url, FEATURE_OFF_TEXT)
        return None

    message = (
        Message.objects.select_related("conversation", "author").filter(pk=message_db_id).first()
    )
    if message is None:
        post_ephemeral_url(response_url, MISSING_MESSAGE_TEXT)
        return None

    try:
        conversation = resolve_conversation(
            client,
            workspace,
            message.conversation.slack_channel_id,
        )
    except ValueError:
        logger.exception(
            "Cannot submit content report for message_id=%s workspace=%s",
            message_db_id,
            workspace.slack_workspace_id,
        )
        post_ephemeral_url(response_url, WORKSPACE_MISMATCH_TEXT)
        return None
    message.conversation = conversation
    author_id = Message.get_author_id(
        message.raw_data if isinstance(message.raw_data, dict) else {}
    )
    if not conversation.has_slack_metadata:
        error = METADATA_UNAVAILABLE_TEXT
    elif conversation.is_private:
        error = PRIVATE_CHANNEL_TEXT
    elif ContentReport.is_self_report(reporter_user_id, author_id):
        error = SELF_REPORT_TEXT
    elif ContentReport.exists_for(conversation, message.slack_message_id):
        error = ALREADY_REPORTED_TEXT
    else:
        error = None

    if error is not None:
        post_ephemeral_url(response_url, error)
        return None

    return workspace, message, reporter_user_id, response_url, source


def post_content_report_alert(
    *,
    client: WebClient,
    message: Message,
    owner: str,
    report_type: str,
    reporter_user_id: str,
    response_url: str,
    source: str,
    workspace: Workspace,
) -> None:
    """Post the moderation alert and record the content report while holding the lock."""
    conversation = message.conversation
    message_ts = message.slack_message_id
    try:
        if not ContentReport.renew(conversation, message_ts, owner):
            post_ephemeral_url(response_url, ALREADY_REPORTED_TEXT)
            return

        permalink = Message.fetch_permalink(client, conversation.slack_channel_id, message_ts)
        text = ContentReport.build_alert_text(
            conversation=conversation,
            message=message,
            permalink=permalink,
            report_type=report_type,
            reporter_user_id=reporter_user_id,
            workspace=workspace,
        )
        channel_id = (workspace.content_report_alert_channel_id or "").strip()
        if ContentReport.post_alert(
            client,
            channel_id=channel_id,
            conversation=conversation,
            message_ts=message_ts,
            message=message,
            reaction_count=None,
            report_type=report_type,
            reporter_user_ids=[reporter_user_id],
            source=source,
            text=text,
        ):
            post_ephemeral_url(response_url, SUCCESS_TEXT)
        else:
            post_ephemeral_url(response_url, SUBMIT_FAILED_TEXT)
    finally:
        ContentReport.release(conversation, message_ts, owner)


class ReportContent(ShortcutBase):
    """Report content message shortcut and modal submission."""

    callback_id = REPORT_CONTENT_CALLBACK_ID
    view_callback_id = REPORT_CONTENT_VIEW_CALLBACK_ID

    def handle(self, ack, shortcut: dict[str, Any], client: WebClient, respond) -> None:
        """Open the Report content modal after applying open-time guards."""
        ack()

        reporter_user_id = (shortcut.get("user") or {}).get("id") or ""
        channel_id = (shortcut.get("channel") or {}).get("id") or ""
        message_payload = shortcut.get("message") or {}
        team_id = (shortcut.get("team") or {}).get("id")
        response_url = shortcut.get("response_url") or ""
        trigger_id = shortcut.get("trigger_id") or ""
        message_ts = message_payload.get("ts") or ""

        if (
            not reporter_user_id
            or not channel_id
            or not message_ts
            or not trigger_id
            or not team_id
        ):
            logger.warning("Ignoring incomplete report_content shortcut payload")
            return

        if (
            workspace := Workspace.get_by_workspace_id(team_id)
        ) is None or not workspace.is_content_reporting_enabled:
            make_ephemeral(respond, response_url)(text=FEATURE_OFF_TEXT)
            return

        open_report_content_modal(
            client=client,
            workspace=workspace,
            channel_id=channel_id,
            message_payload=message_payload,
            reporter_user_id=reporter_user_id,
            response_url=response_url,
            trigger_id=trigger_id,
            source=str(ReportSource.SHORTCUT),
            respond=respond,
        )

    def handle_view(self, ack, body: dict[str, Any], client: WebClient) -> None:
        """Validate consent and category, then post a content-report alert."""
        view = body.get("view") or {}
        report_type = selected_report_type(view)
        has_consent = consent_given(view)
        if not has_consent or report_type is None:
            errors: dict[str, str] = {}
            if not has_consent:
                errors[CONSENT_BLOCK_ID] = (
                    "Please confirm that this message will be shared with workspace moderators."
                )
            if report_type is None:
                errors[REPORT_TYPE_BLOCK_ID] = "Please select a report category."
            ack(response_action="errors", errors=errors)
            return

        ack()
        loaded = load_submission_context(body, client, view)
        if loaded is None:
            return

        workspace, message, reporter_user_id, response_url, source = loaded
        if (
            owner := ContentReport.acquire(message.conversation, message.slack_message_id)
        ) is None:
            post_ephemeral_url(response_url, ALREADY_REPORTED_TEXT)
            return

        post_content_report_alert(
            client=client,
            workspace=workspace,
            message=message,
            reporter_user_id=reporter_user_id,
            response_url=response_url,
            source=source,
            owner=owner,
            report_type=report_type,
        )
