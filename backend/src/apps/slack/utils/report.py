"""Shared open-path helpers for Slack content reporting."""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

from slack_sdk.errors import SlackClientError
from slack_sdk.webhook import WebhookClient

from apps.slack.modals.report import (
    ALREADY_REPORTED_TEXT,
    METADATA_UNAVAILABLE_TEXT,
    MISSING_MESSAGE_TEXT,
    MODAL_OPEN_FAILED_TEXT,
    PRIVATE_CHANNEL_TEXT,
    SELF_REPORT_TEXT,
    build_error_modal,
    build_loading_modal,
    build_report_modal,
)
from apps.slack.models.content_report import ContentReport
from apps.slack.models.conversation import Conversation
from apps.slack.models.member import Member
from apps.slack.models.message import Message

if TYPE_CHECKING:
    from collections.abc import Callable

    from slack_sdk import WebClient

    from apps.slack.enums import ReportSource
    from apps.slack.models.workspace import Workspace

logger = logging.getLogger(__name__)

ALLOWED_RESPONSE_URL_HOSTS = frozenset({"hooks.slack.com"})
CONVERSATION_INFO_TIMEOUT_SECONDS = 1.5
RESPONSE_URL_TIMEOUT_SECONDS = 5
WORKSPACE_MISMATCH_TEXT = (
    "That message belongs to a different Slack workspace and cannot be reported here."
)


def is_allowed_response_url(response_url: str) -> bool:
    """Return True when response_url is an https Slack hooks host."""
    try:
        parsed = urlparse(response_url)
    except ValueError:
        return False
    return parsed.scheme == "https" and parsed.hostname in ALLOWED_RESPONSE_URL_HOSTS


def make_ephemeral(
    respond: Callable[..., Any] | None = None,
    response_url: str = "",
) -> Callable[..., None]:
    """Build an ephemeral sender that prefers Bolt respond, then response_url."""

    def ephemeral(*, text: str) -> None:
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
    """Exchange trigger_id immediately, then fill or replace the report modal."""
    ephemeral = make_ephemeral(respond, response_url)
    author_id = Message.get_author_id(message_payload)
    message_ts = message_payload.get("ts") or ""
    if ContentReport.is_self_report(reporter_user_id, author_id):
        ephemeral(text=SELF_REPORT_TEXT)
        return
    if not message_ts:
        ephemeral(text=MISSING_MESSAGE_TEXT)
        return

    try:
        opened = client.views_open(trigger_id=trigger_id, view=build_loading_modal())
    except SlackClientError:
        logger.exception("Failed to open report_content loading modal")
        ephemeral(text=MODAL_OPEN_FAILED_TEXT)
        return

    view_id = (opened.get("view") or {}).get("id") if opened is not None else None
    if not view_id:
        logger.error("views_open succeeded without a view id for channel_id=%s", channel_id)
        ephemeral(text=MODAL_OPEN_FAILED_TEXT)
        return

    try:
        view = report_modal_view(
            client=client,
            workspace=workspace,
            channel_id=channel_id,
            message_payload=message_payload,
            author_id=author_id,
            message_ts=message_ts,
            response_url=response_url,
            source=source,
        )
    except Exception:
        logger.exception(
            "Failed to build report_content modal for channel_id=%s",
            channel_id,
        )
        view = build_error_modal(MODAL_OPEN_FAILED_TEXT)
    if not update_modal(client, view_id, view):
        ephemeral(text=MODAL_OPEN_FAILED_TEXT)


def post_ephemeral_url(response_url: str, text: str) -> None:
    """Post an ephemeral message via Slack's response_url webhook."""
    if not is_allowed_response_url(response_url):
        logger.warning("Rejected disallowed content-report response_url host")
        return
    try:
        response = WebhookClient(response_url, timeout=RESPONSE_URL_TIMEOUT_SECONDS).send(
            text=text,
            response_type="ephemeral",
        )
    except Exception:
        logger.exception("Failed to post content-report ephemeral response")
        return
    if response.status_code >= HTTPStatus.BAD_REQUEST:
        logger.error(
            "Content-report ephemeral response_url returned status_code=%s body=%s",
            response.status_code,
            response.body,
        )


def report_modal_view(
    *,
    client: WebClient,
    workspace: Workspace,
    channel_id: str,
    message_payload: dict[str, Any],
    author_id: str | None,
    message_ts: str,
    response_url: str,
    source: ReportSource | str,
) -> dict[str, Any]:
    """Build the filled report modal or an error modal after the loading view opens."""
    try:
        conversation = resolve_conversation(client, workspace, channel_id)
    except ValueError:
        logger.exception(
            "Cannot open content report for channel_id=%s workspace=%s",
            channel_id,
            workspace.slack_workspace_id,
        )
        return build_error_modal(WORKSPACE_MISMATCH_TEXT)

    if not conversation.has_slack_metadata:
        return build_error_modal(METADATA_UNAVAILABLE_TEXT)
    if conversation.is_private:
        return build_error_modal(PRIVATE_CHANNEL_TEXT)
    if ContentReport.exists_for(conversation, message_ts):
        return build_error_modal(ALREADY_REPORTED_TEXT)

    author = None
    if isinstance(author_id, str) and author_id:
        author = Member.objects.get_or_create(
            slack_user_id=author_id,
            defaults={"workspace": workspace},
        )[0]
    message = Message.update_data(message_payload, conversation, author=author)
    return build_report_modal(
        message=message,
        conversation=conversation,
        response_url=response_url,
        source=source,
    )


def resolve_conversation(
    client: WebClient,
    workspace: Workspace,
    channel_id: str,
) -> Conversation:
    """Return a conversation, refreshing privacy flags from Slack when needed.

    Skips conversations.info when Slack metadata is already present and fresh so
    a slow refresh cannot burn the views_open trigger_id budget (~3s). Uses a
    short timeout when a refresh is required.

    User-to-user DMs (D-prefixed ids) skip conversations.info: NestBot is not a
    member of those conversations, so the API returns channel_not_found. The id
    prefix is enough to classify them as non-private IMs for content reporting.
    """
    conversation = Conversation.get_or_create(workspace, channel_id)
    if conversation.has_fresh_metadata:
        return conversation
    if conversation.mark_direct_message_metadata():
        return conversation

    try:
        response = client.conversations_info(
            channel=channel_id,
            timeout=CONVERSATION_INFO_TIMEOUT_SECONDS,
        )
    except SlackClientError:
        logger.warning(
            "Could not load conversation metadata for channel_id=%s",
            channel_id,
            exc_info=True,
        )
        return conversation

    channel = response.get("channel") if response is not None else None
    if not isinstance(channel, dict) or not channel.get("id"):
        return conversation
    return Conversation.update_data(channel, workspace, save=True)


def update_modal(client: WebClient, view_id: str, view: dict[str, Any]) -> bool:
    """Replace an open modal view. Return False when Slack rejects the update."""
    try:
        client.views_update(view_id=view_id, view=view)
    except SlackClientError:
        logger.exception("Failed to update report_content modal view_id=%s", view_id)
        return False
    return True
