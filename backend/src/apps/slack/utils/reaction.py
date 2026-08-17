"""Slack reaction event helpers."""


def format_emojis(emojis: object) -> str:
    """Return Slack emoji markup for the given emoji names."""
    if not emojis or not isinstance(emojis, list):
        return ""
    return " ".join(f":{name}:" for name in emojis if name)


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


def reaction_from_payload(payload, emojis: object) -> tuple[int, list[str], str] | None:
    """Return unique reporter IDs and permalink for listed emojis on a reactions.get payload."""
    if not isinstance(emojis, list):
        return None
    wanted = {name for name in emojis if name}
    if not wanted:
        return None

    message = payload.get("message") or {}
    permalink = message.get("permalink") or ""
    reporters: list[str] = []
    seen: set[str] = set()
    matched = False
    for reaction in message.get("reactions") or []:
        if reaction.get("name") not in wanted:
            continue
        matched = True
        for user_id in reaction.get("users") or []:
            if user_id and user_id not in seen:
                seen.add(user_id)
                reporters.append(user_id)
    if not matched:
        return None
    return len(reporters), reporters, permalink
