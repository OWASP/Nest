"""Slack service tasks for background processing."""

import logging

from django_rq import job
from slack_sdk.errors import SlackApiError

from apps.slack.apps import SlackConfig
from apps.slack.common.handlers.ai import format_blocks, process_ai_query
from apps.slack.models import Message

logger = logging.getLogger(__name__)


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
    
    # Add 👀 reaction to show we are working on it
    try:
        client.reactions_add(
            channel=channel_id,
            timestamp=message.slack_message_id,
            name="eyes",
        )
    except SlackApiError:
        pass

    ai_response_text = process_ai_query(query=message.text, channel_id=channel_id)
    
    if not ai_response_text:
        # Remove eyes reaction and add shrugging reaction when no answer can be generated
        try:
            # Remove eyes reaction if it exists
            client.reactions_remove(
                channel=channel_id,
                timestamp=message.slack_message_id,
                name="eyes",
            )
        except SlackApiError:
            # Ignore if eyes reaction doesn't exist
            pass
        
        try:
            result = client.reactions_add(
                channel=channel_id,
                timestamp=message.slack_message_id,
                name="man-shrugging",
            )
            if result.get("ok"):
                logger.info("Successfully added 🤷 reaction to message")
            else:
                error = result.get("error")
                if error != "already_reacted":
                    logger.warning(
                        "Failed to add reaction: %s",
                        error,
                        extra={
                            "channel_id": channel_id,
                            "message_id": message.slack_message_id,
                        },
                    )
        except SlackApiError:
            logger.exception("Error adding reaction to message")
        return

    client.chat_postMessage(
        channel=channel_id,
        blocks=format_blocks(ai_response_text),
        text=ai_response_text,
        thread_ts=message.slack_message_id,
    )

    # Remove 👀 reaction and add ✅ reaction to show we are done
    try:
        # Remove eyes reaction if it exists
        client.reactions_remove(
            channel=channel_id,
            timestamp=message.slack_message_id,
            name="eyes",
        )
    except SlackApiError:
        # Ignore if eyes reaction doesn't exist
        pass
    
    try:
        client.reactions_add(
            channel=channel_id,
            timestamp=message.slack_message_id,
            name="white_check_mark",
        )
    except SlackApiError:
        pass


@job("ai")
def process_ai_query_async(
    query: str,
    channel_id: str,
    message_ts: str,
    thread_ts: str = None,
    is_app_mention: bool = False,
    user_id: str = None,
):
    """Process an AI query asynchronously (app mention or slash command)."""
    if not SlackConfig.app:
        logger.warning("Slack app is not configured")
        return

    client = SlackConfig.app.client

    ai_response_text = process_ai_query(
        query=query, channel_id=channel_id, is_app_mention=is_app_mention
    )

    if not ai_response_text:
        # Remove eyes reaction and add shrugging reaction when no answer can be generated
        try:
            # Remove eyes reaction if it exists
            client.reactions_remove(
                channel=channel_id,
                timestamp=message_ts,
                name="eyes",
            )
        except SlackApiError:
            # Ignore if eyes reaction doesn't exist
            pass
        
        try:
            client.reactions_add(
                channel=channel_id,
                timestamp=message_ts,
                name="man-shrugging",
            )
        except SlackApiError:
            pass

        # If it's a slash command, we might want to send an ephemeral error
        if not is_app_mention and user_id:
            try:
                client.chat_postEphemeral(
                    channel=channel_id,
                    user=user_id,
                    text="⚠️ I was unable to generate a response. Please try again later.",
                )
            except SlackApiError:
                pass
        return

    # Post the response
    client.chat_postMessage(
        channel=channel_id,
        blocks=format_blocks(ai_response_text),
        text=ai_response_text,
        thread_ts=thread_ts or message_ts,
    )

    # Remove 👀 reaction and add ✅ reaction to show we are done
    if message_ts:
        try:
            # Remove eyes reaction if it exists
            client.reactions_remove(
                channel=channel_id,
                timestamp=message_ts,
                name="eyes",
            )
        except SlackApiError:
            # Ignore if eyes reaction doesn't exist
            pass
        
        try:
            client.reactions_add(
                channel=channel_id,
                timestamp=message_ts,
                name="white_check_mark",
            )
        except SlackApiError:
            pass
