"""Slack reaction event helpers."""


def mention_users(user_ids: object) -> str:
    """Return Slack mention markup for the given user IDs."""
    if not user_ids or not isinstance(user_ids, list):
        return ""
    return " ".join(f"<@{user_id}>" for user_id in user_ids if user_id)


def parse_message_reaction(event):
    """Return channel, message timestamp, and emoji for a message reaction event."""
    item = event.get("item", {})
    channel_id = item.get("channel")
    emoji_name = event.get("reaction")
    message_ts = item.get("ts")
    if (
        item.get("type") != "message"
        or not channel_id
        or not emoji_name
        or not message_ts
        or not event.get("user")
    ):
        return None
    return channel_id, message_ts, emoji_name
