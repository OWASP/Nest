"""Slack message shortcut and shared content-report handlers."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import requests
from slack_sdk.errors import SlackApiError

from apps.slack.apps import SlackConfig
from apps.slack.enums import ReportSource
from apps.slack.models.content_report import ContentReport
from apps.slack.models.conversation import Conversation
from apps.slack.models.member import Member
from apps.slack.models.message import Message
from apps.slack.models.workspace import Workspace
from apps.slack.utils.report_modal import (
    ALREADY_REPORTED_TEXT,
    CONSENT_BLOCK_ID,
    FEATURE_OFF_TEXT,
    MISSING_MESSAGE_TEXT,
    MODAL_OPEN_FAILED_TEXT,
    REPORT_CONTENT_CALLBACK_ID,
    REPORT_CONTENT_VIEW_CALLBACK_ID,
    REPORT_TYPE_BLOCK_ID,
    SELF_REPORT_TEXT,
    SUBMIT_FAILED_TEXT,
    SUCCESS_TEXT,
    build_report_modal,
    consent_given,
    decode_metadata,
    selected_report_type,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from slack_sdk import WebClient

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SubmissionContext:
    """Validated modal submission context for posting a content report."""

    workspace: Workspace
    message: Message
    conversation: Conversation
    reporter_user_id: str
    response_url: str
    source: str


def post_ephemeral_url(response_url: str, text: str) -> None:
    """Post an ephemeral message to a Slack response_url."""
    try:
        requests.post(
            response_url,
            json={"text": text, "response_type": "ephemeral"},
            timeout=5,
        )
    except requests.RequestException:
        logger.exception("Failed to post content-report ephemeral response")


def make_ephemeral(
    respond: Callable[..., Any] | None = None,
    response_url: str = "",
) -> Callable[..., None]:
    """Build an ephemeral sender that prefers Bolt respond, then response_url."""

    def ephemeral(*, text: str, response_type: str = "ephemeral") -> None:  # noqa: ARG001
        if respond is not None:
            respond(text=text, response_type="ephemeral")
            return
        if response_url:
            post_ephemeral_url(response_url, text)

    return ephemeral


def open_report_content_modal(
    *,
    client: WebClient,
    workspace: Workspace,
    channel_id: str,
    message_payload: dict[str, Any],
    reporter_user_id: str,
    response_url: str,
    trigger_id: str,
    source: ReportSource | str,
    respond: Callable[..., Any] | None = None,
) -> None:
    """Apply open-time guards, upsert the message, and open the report modal."""
    ephemeral = make_ephemeral(respond, response_url)
    author_id = Message.get_author_id(message_payload)
    if ContentReport.is_self_report(reporter_user_id, author_id):
        ephemeral(text=SELF_REPORT_TEXT)
        return

    message_ts = message_payload.get("ts") or ""
    if not message_ts:
        ephemeral(text=MISSING_MESSAGE_TEXT)
        return

    conversation = Conversation.get_or_create_for_report(workspace, channel_id)
    if ContentReport.exists_for(conversation, message_ts):
        ephemeral(text=ALREADY_REPORTED_TEXT)
        return

    author = None
    if isinstance(author_id, str) and author_id:
        author, _ = Member.objects.get_or_create(
            slack_user_id=author_id,
            defaults={"workspace": workspace},
        )
    message = Message.update_data(message_payload, conversation, author=author)
    try:
        client.views_open(
            trigger_id=trigger_id,
            view=build_report_modal(
                message=message,
                conversation=conversation,
                response_url=response_url,
                source=source,
            ),
        )
    except SlackApiError:
        logger.exception("Failed to open report_content modal")
        ephemeral(text=MODAL_OPEN_FAILED_TEXT)


def load_submission_context(
    body: dict[str, Any],
    view: dict[str, Any],
) -> SubmissionContext | None:
    """Validate submission payload and return report context, or None after ephemeral errors."""
    reporter_user_id = (body.get("user") or {}).get("id") or ""
    team_id = (body.get("team") or {}).get("id") or view.get("team_id")
    metadata = decode_metadata(view.get("private_metadata") or "")
    if metadata is None or not reporter_user_id or not team_id:
        logger.warning("Ignoring invalid report_content submission")
        return None

    message_db_id, response_url, source = metadata
    workspace = Workspace.get_by_workspace_id(team_id)
    if workspace is None or not workspace.is_content_reporting_enabled:
        post_ephemeral_url(response_url, FEATURE_OFF_TEXT)
        return None

    try:
        message = Message.objects.select_related("conversation", "author").get(pk=message_db_id)
    except Message.DoesNotExist:
        post_ephemeral_url(response_url, MISSING_MESSAGE_TEXT)
        return None

    conversation = message.conversation
    author_id = Message.get_author_id(
        message.raw_data if isinstance(message.raw_data, dict) else {}
    )
    if ContentReport.is_self_report(reporter_user_id, author_id):
        post_ephemeral_url(response_url, SELF_REPORT_TEXT)
        return None
    if ContentReport.exists_for(conversation, message.slack_message_id):
        post_ephemeral_url(response_url, ALREADY_REPORTED_TEXT)
        return None

    return SubmissionContext(
        workspace=workspace,
        message=message,
        conversation=conversation,
        reporter_user_id=reporter_user_id,
        response_url=response_url,
        source=source,
    )


def post_content_report_alert(
    *,
    client: WebClient,
    context: SubmissionContext,
    owner: str,
    report_type: str,
) -> None:
    """Post the moderation alert and record the content report while holding the lock."""
    message = context.message
    conversation = context.conversation
    message_ts = message.slack_message_id
    try:
        if not ContentReport.renew(conversation, message_ts, owner):
            post_ephemeral_url(context.response_url, ALREADY_REPORTED_TEXT)
            return

        permalink = Message.fetch_permalink(client, conversation.slack_channel_id, message_ts)
        text = ContentReport.build_alert_text(
            workspace=context.workspace,
            conversation=conversation,
            message=message,
            reporter_user_id=context.reporter_user_id,
            report_type=report_type,
            permalink=permalink,
        )
        channel_id = (context.workspace.content_report_alert_channel_id or "").strip()
        if ContentReport.deliver_alert(
            client,
            channel_id=channel_id,
            text=text,
            conversation=conversation,
            message_ts=message_ts,
            report_type=report_type,
            source=context.source,
            reporter_user_ids=[context.reporter_user_id],
            reaction_count=None,
            message=message,
        ):
            post_ephemeral_url(context.response_url, SUCCESS_TEXT)
        else:
            post_ephemeral_url(context.response_url, SUBMIT_FAILED_TEXT)
    finally:
        ContentReport.release(conversation, message_ts, owner)


def handle_report_content_shortcut(
    ack,
    shortcut: dict[str, Any],
    client: WebClient,
    respond,
) -> None:
    """Open the Report content modal after applying open-time guards."""
    ack()

    reporter_user_id = (shortcut.get("user") or {}).get("id") or ""
    channel_id = (shortcut.get("channel") or {}).get("id") or ""
    message_payload = shortcut.get("message") or {}
    team_id = (shortcut.get("team") or {}).get("id")
    response_url = shortcut.get("response_url") or ""
    trigger_id = shortcut.get("trigger_id") or ""
    message_ts = message_payload.get("ts") or ""

    if not reporter_user_id or not channel_id or not message_ts or not trigger_id or not team_id:
        logger.warning("Ignoring incomplete report_content shortcut payload")
        return

    workspace = Workspace.get_by_workspace_id(team_id)
    if workspace is None or not workspace.is_content_reporting_enabled:
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


def handle_report_content_submission(ack, body: dict[str, Any], client: WebClient) -> None:
    """Validate consent and category, then post a workspace content-report alert."""
    view = body.get("view") or {}
    report_type = selected_report_type(view)
    if not consent_given(view) or report_type is None:
        errors: dict[str, str] = {}
        if not consent_given(view):
            errors[CONSENT_BLOCK_ID] = (
                "Please confirm that this message will be shared with workspace moderators."
            )
        if report_type is None:
            errors[REPORT_TYPE_BLOCK_ID] = "Please select a report category."
        ack(response_action="errors", errors=errors)
        return

    ack()
    context = load_submission_context(body, view)
    if context is None:
        return

    if (
        owner := ContentReport.acquire(context.conversation, context.message.slack_message_id)
    ) is None:
        post_ephemeral_url(context.response_url, ALREADY_REPORTED_TEXT)
        return

    post_content_report_alert(
        client=client,
        context=context,
        owner=owner,
        report_type=report_type,
    )


if SlackConfig.app:
    SlackConfig.app.shortcut(REPORT_CONTENT_CALLBACK_ID)(handle_report_content_shortcut)
    SlackConfig.app.view(REPORT_CONTENT_VIEW_CALLBACK_ID)(handle_report_content_submission)
