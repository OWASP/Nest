"""Slack service tasks for background processing."""

import base64
import contextlib
import logging

from django_rq import job
from slack_sdk.errors import SlackApiError

from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown_blocks
from apps.slack.common.handlers.ai import process_ai_query
from apps.slack.models import Message
from apps.slack.utils import (
    download_file,
    format_ai_response_for_slack,
    truncate_for_slack_fallback,
)

logger = logging.getLogger(__name__)

ERROR_UNABLE_TO_GENERATE_RESPONSE = (
    "⚠️ I was unable to generate a response. Please try again later."
)
ERROR_POSTING_RESPONSE = "⚠️ An error occurred while posting the response. Please try again later."
ERROR_UNEXPECTED_PROCESSING = (
    "⚠️ An unexpected error occurred while processing your query. Please try again later."
)


def _format_response_blocks(text: str) -> list[dict]:
    """Format final AI response as Slack blocks."""
    return markdown_blocks(format_ai_response_for_slack(text))


def _slack_files_to_image_uris(client, slack_image_files: list[dict]) -> list[str] | None:
    """Download Slack-hosted files in the worker and build data URIs for vision flow."""
    uris: list[str] = []
    for file in slack_image_files:
        url = file.get("url_private")
        mime = file.get("mimetype") or "application/octet-stream"
        if not url:
            continue
        content = download_file(url, client.token)
        if content:
            uris.append(f"data:{mime};base64,{base64.b64encode(content).decode()}")
    return uris or None


def _post_slash_command_dm(
    client,
    user_id: str,
    *,
    blocks: list[dict],
    fallback_text: str,
) -> None:
    """Post AI reply to the user's DM (matches legacy /ai private behavior)."""
    try:
        conv = client.conversations_open(users=user_id)
        dm_id = conv["channel"]["id"]
    except SlackApiError:
        logger.exception(
            "Failed to open DM for slash command reply",
            extra={"user_id": user_id},
        )
        return
    try:
        client.chat_postMessage(
            channel=dm_id,
            blocks=blocks,
            text=fallback_text,
        )
    except SlackApiError:
        logger.exception(
            "Failed to post slash command reply to DM",
            extra={"user_id": user_id},
        )


@job("ai")
def generate_ai_reply_if_unanswered(message_id: int):
    """Check if a message is still unanswered and generate AI reply."""
    try:
        message = Message.objects.get(pk=message_id)
    except Message.DoesNotExist:
        return

    if not message.conversation.is_nest_bot_assistant_enabled:
        return

    if not SlackConfig.app:
        logger.warning("Slack app is not configured")
        return

    client = SlackConfig.app.client

    try:
        result = client.conversations_replies(
            channel=message.conversation.slack_channel_id,
            ts=message.slack_message_id,
            limit=1,
        )
        if result.get("messages") and result["messages"][0].get("reply_count", 0) > 0:
            return
    except SlackApiError:
        logger.exception("Error checking for replies for message")

    channel_id = message.conversation.slack_channel_id
    message_ts = message.slack_message_id

    with contextlib.suppress(SlackApiError):
        client.reactions_add(
            channel=channel_id,
            timestamp=message_ts,
            name="eyes",
        )

    thinking_ts = None
    try:
        result = client.chat_postMessage(
            channel=channel_id,
            text="Thinking...",
            thread_ts=message_ts,
        )
        thinking_ts = result.get("ts")
    except SlackApiError:
        logger.exception("Error posting thinking message")

    try:
        ai_response_text = process_ai_query(query=message.text, channel_id=channel_id)

        if not ai_response_text:
            with contextlib.suppress(SlackApiError):
                client.reactions_remove(
                    channel=channel_id,
                    timestamp=message_ts,
                    name="eyes",
                )

            try:
                client.reactions_add(
                    channel=channel_id,
                    timestamp=message_ts,
                    name="man-shrugging",
                )
            except SlackApiError as e:
                if e.response.get("error") != "already_reacted":
                    logger.warning(
                        "Failed to add no-answer reaction: %s",
                        e.response.get("error"),
                        extra={"channel_id": channel_id, "message_ts": message_ts},
                    )

            with contextlib.suppress(SlackApiError):
                client.chat_postMessage(
                    channel=channel_id,
                    text=ERROR_UNABLE_TO_GENERATE_RESPONSE,
                    thread_ts=message_ts,
                )
            return

        blocks = _format_response_blocks(ai_response_text)
        client.chat_postMessage(
            channel=channel_id,
            blocks=blocks,
            text=truncate_for_slack_fallback(ai_response_text),
            thread_ts=message_ts,
        )

        with contextlib.suppress(SlackApiError):
            client.reactions_remove(
                channel=channel_id,
                timestamp=message_ts,
                name="eyes",
            )
    except (ValueError, SlackApiError):
        logger.exception(
            "Error posting AI response",
            extra={"channel_id": channel_id, "message_ts": message_ts},
        )
        with contextlib.suppress(SlackApiError):
            client.chat_postMessage(
                channel=channel_id,
                text=ERROR_POSTING_RESPONSE,
                thread_ts=message_ts,
            )
        with contextlib.suppress(SlackApiError):
            client.reactions_remove(
                channel=channel_id,
                timestamp=message_ts,
                name="eyes",
            )
    except Exception:
        logger.exception(
            "Unexpected error processing AI query",
            extra={"channel_id": channel_id, "message_ts": message_ts},
        )
        with contextlib.suppress(SlackApiError):
            client.chat_postMessage(
                channel=channel_id,
                text=ERROR_UNEXPECTED_PROCESSING,
                thread_ts=message_ts,
            )
        with contextlib.suppress(SlackApiError):
            client.reactions_remove(
                channel=channel_id,
                timestamp=message_ts,
                name="eyes",
            )
    finally:
        if thinking_ts:
            with contextlib.suppress(SlackApiError):
                client.chat_delete(channel=channel_id, ts=thinking_ts)


@job("ai")
def process_ai_query_async(
    query: str,
    channel_id: str,
    message_ts: str | None,
    thread_ts: str | None = None,
    *,
    is_app_mention: bool = False,
    user_id: str | None = None,
    images: list[str] | None = None,
    slack_image_files: list[dict] | None = None,
):
    """Process an AI query asynchronously (app mention or slash command)."""
    if not SlackConfig.app:
        logger.warning("Slack app is not configured")
        return

    client = SlackConfig.app.client
    thinking_ts = None

    image_uris = images
    if slack_image_files:
        image_uris = _slack_files_to_image_uris(client, slack_image_files)

    if message_ts:
        try:
            result = client.chat_postMessage(
                channel=channel_id,
                text="Thinking...",
                thread_ts=thread_ts or message_ts,
            )
            thinking_ts = result.get("ts")
        except SlackApiError:
            logger.exception("Error posting thinking message")

    try:
        ai_response_text = process_ai_query(
            query=query,
            images=image_uris,
            channel_id=channel_id,
            is_app_mention=is_app_mention,
        )

        if not ai_response_text:
            if message_ts:
                with contextlib.suppress(SlackApiError):
                    client.reactions_remove(
                        channel=channel_id,
                        timestamp=message_ts,
                        name="eyes",
                    )
                with contextlib.suppress(SlackApiError):
                    client.reactions_add(
                        channel=channel_id,
                        timestamp=message_ts,
                        name="man-shrugging",
                    )

            if is_app_mention:
                with contextlib.suppress(SlackApiError):
                    client.chat_postMessage(
                        channel=channel_id,
                        text=ERROR_UNABLE_TO_GENERATE_RESPONSE,
                        thread_ts=thread_ts or message_ts,
                    )
            elif user_id:
                with contextlib.suppress(SlackApiError):
                    client.chat_postEphemeral(
                        channel=channel_id,
                        user=user_id,
                        text=ERROR_UNABLE_TO_GENERATE_RESPONSE,
                    )
            return

        blocks = _format_response_blocks(ai_response_text)
        fallback = truncate_for_slack_fallback(ai_response_text)
        if user_id and not message_ts and not is_app_mention:
            _post_slash_command_dm(
                client,
                user_id,
                blocks=blocks,
                fallback_text=fallback,
            )
        else:
            client.chat_postMessage(
                channel=channel_id,
                blocks=blocks,
                text=fallback,
                thread_ts=thread_ts or message_ts,
            )

        if message_ts:
            with contextlib.suppress(SlackApiError):
                client.reactions_remove(
                    channel=channel_id,
                    timestamp=message_ts,
                    name="eyes",
                )
    except SlackApiError:
        logger.exception(
            "Error posting AI response",
            extra={"channel_id": channel_id, "message_ts": message_ts},
        )
        if is_app_mention:
            with contextlib.suppress(SlackApiError):
                client.chat_postMessage(
                    channel=channel_id,
                    text=ERROR_POSTING_RESPONSE,
                    thread_ts=thread_ts or message_ts,
                )
        elif user_id:
            with contextlib.suppress(SlackApiError):
                client.chat_postEphemeral(
                    channel=channel_id,
                    user=user_id,
                    text=ERROR_POSTING_RESPONSE,
                )

        if message_ts:
            with contextlib.suppress(SlackApiError):
                client.reactions_remove(
                    channel=channel_id,
                    timestamp=message_ts,
                    name="eyes",
                )
    except Exception:
        logger.exception(
            "Unexpected error processing AI query",
            extra={"channel_id": channel_id, "message_ts": message_ts},
        )
        if is_app_mention:
            with contextlib.suppress(SlackApiError):
                client.chat_postMessage(
                    channel=channel_id,
                    text=ERROR_UNEXPECTED_PROCESSING,
                    thread_ts=thread_ts or message_ts,
                )
        elif user_id:
            with contextlib.suppress(SlackApiError):
                client.chat_postEphemeral(
                    channel=channel_id,
                    user=user_id,
                    text=ERROR_UNEXPECTED_PROCESSING,
                )

        if message_ts:
            with contextlib.suppress(SlackApiError):
                client.reactions_remove(
                    channel=channel_id,
                    timestamp=message_ts,
                    name="eyes",
                )
    finally:
        if thinking_ts:
            with contextlib.suppress(SlackApiError):
                client.chat_delete(channel=channel_id, ts=thinking_ts)
