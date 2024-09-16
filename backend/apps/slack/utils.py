"""Slack app utils."""

import html


def escape(content):
    """Escape HTML content."""
    return html.escape(content, quote=False)
