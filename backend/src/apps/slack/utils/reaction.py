"""Slack reaction event helpers."""


def mention_users(user_ids) -> str:
    """Return Slack mention markup for the given user IDs."""
    return " ".join(f"<@{user_id}>" for user_id in user_ids or [])


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


def reaction_from_payload(payload, emoji_name: str) -> tuple[int, list[str], str] | None:
    """Return count, reporter IDs, and permalink for an emoji on a reactions.get payload."""
    message = payload.get("message") or {}
    permalink = message.get("permalink") or ""
    for reaction in message.get("reactions") or []:
        if reaction.get("name") != emoji_name:
            continue
        reporter_user_ids = list(reaction.get("users") or [])
        count = reaction.get("count")
        reaction_count = int(count) if count is not None else len(reporter_user_ids)
        return reaction_count, reporter_user_ids, permalink
    return None
