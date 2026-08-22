"""Shared open-path helpers for Slack content reporting."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

import requests
from slack_sdk.errors import SlackClientError

from apps.slack.models.content_report import ContentReport
from apps.slack.models.conversation import Conversation
from apps.slack.models.member import Member
from apps.slack.models.message import Message
from apps.slack.utils.report_modal import (
    ALREADY_REPORTED_TEXT,
    MISSING_MESSAGE_TEXT,
    MODAL_OPEN_FAILED_TEXT,
    SELF_REPORT_TEXT,
    build_report_modal,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from slack_sdk import WebClient

    from apps.slack.enums import ReportSource
    from apps.slack.models.workspace import Workspace

logger = logging.getLogger(__name__)

ALLOWED_RESPONSE_URL_HOSTS = frozenset({"hooks.slack.com"})


def is_allowed_response_url(response_url: str) -> bool:
    """Return True when response_url is an https Slack hooks host."""
    try:
        parsed = urlparse(response_url)
    except ValueError:
        return False
    return parsed.scheme == "https" and parsed.hostname in ALLOWED_RESPONSE_URL_HOSTS


def post_ephemeral_url(response_url: str, text: str) -> None:
    """Post an ephemeral message to a Slack response_url."""
    if not is_allowed_response_url(response_url):
        logger.warning("Rejected disallowed content-report response_url host")
        return
    try:
        response = requests.post(
            response_url,
            json={"text": text, "response_type": "ephemeral"},
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException:
        logger.exception("Failed to post content-report ephemeral response")


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
    except SlackClientError:
        logger.exception("Failed to open report_content modal")
        ephemeral(text=MODAL_OPEN_FAILED_TEXT)
