"""Slack blocks."""


def divider():
    """Return divider block."""
    return {"type": "divider"}


def markdown(text):
    """Return markdown block."""
    return {
        "type": "section",
        "text": {"type": "mrkdwn", "text": text},
    }
