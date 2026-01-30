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

    # Post a thinking message to let users know we're processing
    thinking_ts = None
    try:
        result = client.chat_postMessage(
            channel=channel_id,
            text="Thinking...",
            thread_ts=message.slack_message_id,
        )
        thinking_ts = result.get("ts")
    except SlackApiError:
        logger.exception("Error posting thinking message")

    try:
        ai_response_text = process_ai_query(query=message.text, channel_id=channel_id)
        
        # Validate response - if it's just "YES" or "NO", something went wrong
        if ai_response_text:
            response_str = str(ai_response_text).strip()
            response_upper = response_str.upper()
            if response_upper == "YES" or response_upper == "NO":
                logger.error(
                    "AI query returned Question Detector output instead of agent response",
                    extra={
                        "channel_id": channel_id,
                        "message_id": message.slack_message_id,
                        "response": response_str,
                    },
                )
                ai_response_text = None
        
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
                if not result.get("ok"):
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
            
            # Post error message to user
            try:
                client.chat_postMessage(
                    channel=channel_id,
                    text="⚠️ I was unable to generate a response. Please try again later.",
                    thread_ts=message.slack_message_id,
                )
            except SlackApiError:
                logger.exception("Error posting error message")
            return

        # Final validation before posting - double check we don't have "YES" or "NO"
        if ai_response_text:
            response_str = str(ai_response_text).strip()
            if response_str.upper() in ("YES", "NO"):
                logger.error(
                    "Attempted to post Question Detector output, blocking",
                    extra={"channel_id": channel_id, "message_id": message.slack_message_id},
                )
                ai_response_text = None

        # Post the response
        if not ai_response_text:
            # Post error message instead
            try:
                client.chat_postMessage(
                    channel=channel_id,
                    text="⚠️ I was unable to generate a response. Please try again later.",
                    thread_ts=message.slack_message_id,
                )
            except SlackApiError:
                logger.exception("Error posting error message")
            return

        try:
            # One more validation check right before formatting
            if ai_response_text:
                response_str = str(ai_response_text).strip()
                if response_str.upper() in ("YES", "NO"):
                    logger.error(
                        "Blocking Question Detector output before formatting",
                        extra={"channel_id": channel_id, "message_id": message.slack_message_id},
                    )
                    raise ValueError("Invalid response: Question Detector output detected")
            
            blocks = format_blocks(ai_response_text)
            result = client.chat_postMessage(
                channel=channel_id,
                blocks=blocks,
                text=ai_response_text,
                thread_ts=message.slack_message_id,
            )
        except (ValueError, SlackApiError) as e:
            logger.exception(
                "Error posting AI response",
                extra={
                    "channel_id": channel_id,
                    "message_id": message.slack_message_id,
                    "error": str(e),
                },
            )
            # Post error message to user
            try:
                client.chat_postMessage(
                    channel=channel_id,
                    text="⚠️ An error occurred while posting the response. Please try again later.",
                    thread_ts=message.slack_message_id,
                )
            except SlackApiError:
                logger.exception("Error posting error message")

        # Remove 👀 reaction to show we are done
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

    except Exception as e:
        logger.exception(
            "Unexpected error processing AI query",
            extra={"channel_id": channel_id, "message_id": message.slack_message_id, "error": str(e)},
        )
        # Post error message to user
        try:
            client.chat_postMessage(
                channel=channel_id,
                text="⚠️ An unexpected error occurred while processing your query. Please try again later.",
                thread_ts=message.slack_message_id,
            )
        except SlackApiError:
            logger.exception("Error posting error message")
        
        # Remove eyes reaction
        try:
            client.reactions_remove(
                channel=channel_id,
                timestamp=message.slack_message_id,
                name="eyes",
            )
        except SlackApiError:
            pass
    finally:
        # Always remove the thinking message if it was posted
        if thinking_ts:
            try:
                client.chat_delete(
                    channel=channel_id,
                    ts=thinking_ts,
                )
            except SlackApiError as e:
                logger.exception(
                    "Error deleting thinking message",
                    extra={"channel_id": channel_id, "thinking_ts": thinking_ts, "error": str(e)},
                )


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

    # Post a thinking message to let users know we're processing
    thinking_ts = None
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
            query=query, channel_id=channel_id, is_app_mention=is_app_mention
        )
        
        # Validate response - if it's just "YES" or "NO", something went wrong
        if ai_response_text:
            response_str = str(ai_response_text).strip()
            if response_str.upper() in ("YES", "NO"):
                logger.error(
                    "AI query returned Question Detector output instead of agent response",
                    extra={"channel_id": channel_id, "message_ts": message_ts},
                )
                ai_response_text = None

        if not ai_response_text:
            # Remove eyes reaction and add shrugging reaction when no answer can be generated
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
                        name="man-shrugging",
                    )
                except SlackApiError:
                    pass

            # Post error message
            if is_app_mention:
                # For app mentions, post in thread
                try:
                    client.chat_postMessage(
                        channel=channel_id,
                        text="⚠️ I was unable to generate a response. Please try again later.",
                        thread_ts=thread_ts or message_ts,
                    )
                except SlackApiError:
                    logger.exception("Error posting error message")
            elif user_id:
                # For slash commands, send ephemeral
                try:
                    client.chat_postEphemeral(
                        channel=channel_id,
                        user=user_id,
                        text="⚠️ I was unable to generate a response. Please try again later.",
                    )
                except SlackApiError:
                    logger.exception("Error posting ephemeral error message")
            return

        # Post the response
        try:
            blocks = format_blocks(ai_response_text)
            logger.debug(
                "Formatted blocks for posting",
                extra={
                    "channel_id": channel_id,
                    "message_ts": message_ts,
                    "blocks_count": len(blocks),
                    "blocks": blocks,
                },
            )
            result = client.chat_postMessage(
                channel=channel_id,
                blocks=blocks,
                text=ai_response_text,
                thread_ts=thread_ts or message_ts,
            )
        except SlackApiError as e:
            logger.exception(
                "Error posting AI response",
                extra={"channel_id": channel_id, "message_ts": message_ts, "error": str(e)},
            )
            # Post error message to user
            if is_app_mention:
                try:
                    client.chat_postMessage(
                        channel=channel_id,
                        text="⚠️ An error occurred while posting the response. Please try again later.",
                        thread_ts=thread_ts or message_ts,
                    )
                except SlackApiError:
                    logger.exception("Error posting error message")
            elif user_id:
                try:
                    client.chat_postEphemeral(
                        channel=channel_id,
                        user=user_id,
                        text="⚠️ An error occurred while posting the response. Please try again later.",
                    )
                except SlackApiError:
                    logger.exception("Error posting ephemeral error message")

        # Remove 👀 reaction to show we are done
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

    except Exception as e:
        logger.exception(
            "Unexpected error processing AI query",
            extra={"channel_id": channel_id, "message_ts": message_ts, "error": str(e)},
        )
        # Post error message to user
        if is_app_mention:
            try:
                client.chat_postMessage(
                    channel=channel_id,
                    text="⚠️ An unexpected error occurred while processing your query. Please try again later.",
                    thread_ts=thread_ts or message_ts,
                )
            except SlackApiError:
                logger.exception("Error posting error message")
        elif user_id:
            try:
                client.chat_postEphemeral(
                    channel=channel_id,
                    user=user_id,
                    text="⚠️ An unexpected error occurred while processing your query. Please try again later.",
                )
            except SlackApiError:
                logger.exception("Error posting ephemeral error message")
        
        # Remove eyes reaction
        if message_ts:
            try:
                client.reactions_remove(
                    channel=channel_id,
                    timestamp=message_ts,
                    name="eyes",
                )
            except SlackApiError:
                pass
    finally:
        # Always remove the thinking message if it was posted
        if thinking_ts:
            try:
                client.chat_delete(
                    channel=channel_id,
                    ts=thinking_ts,
                )
            except SlackApiError as e:
                logger.exception(
                    "Error deleting thinking message",
                    extra={"channel_id": channel_id, "thinking_ts": thinking_ts, "error": str(e)},
                )
