"""NestBot file downloads and AI response formatting."""

from __future__ import annotations

import logging
import re

import requests

from apps.slack.common.text import format_links_for_slack

logger: logging.Logger = logging.getLogger(__name__)


def download_file(url: str, token: str) -> bytes | None:
    """Download Slack file.

    Args:
        url (str): The url of the file.
        token (str): The slack bot token.

    Returns:
        bytes or None: The downloaded file content, or None if download failed.

    """
    if not url or not token:
        return None

    try:
        response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.exception("Failed to download Slack file", extra={"error": str(e)})
        return None

    return response.content


def format_ai_response_for_slack(text: str) -> str:
    """Format AI response text for Slack by removing code blocks and fixing markdown.

    Args:
        text (str): The AI response text that may contain markdown code blocks.

    Returns:
        str: Text formatted for Slack mrkdwn format.

    """
    if not text:
        return text

    # Remove heading emphasis before adding Slack's outer bold markers.
    def replace_heading(match: re.Match[str]) -> str:
        """Apply outer Slack bold without reinterpreting inline code or stray emphasis."""
        content = "".join(
            section if index % 2 else re.sub(r"__(.+?)__", r"\1", section).replace("*", "")
            for index, section in enumerate(re.split(r"(`[^`]+`)", match.group(1).strip()))
        )
        return f"*{content}*"

    def format_text_section(content: str) -> str:
        """Translate prose Markdown while preserving syntax inside literal code spans."""
        content = re.sub(r"```+", "", content)
        content = re.sub(
            r"^#{1,6}[ \t]+([^\s][^\r\n]*)\r?$", replace_heading, content, flags=re.MULTILINE
        )
        sections = []
        for index, section in enumerate(re.split(r"(`[^`]+`)", content)):
            formatted = section
            if index % 2:
                # Keep Slack code delimiters when removing them would activate formatting.
                literal = section[1:-1]
                if not re.search(r"[*_~]|<[@#!]|\[[^\]]+\]\(|<(?:https?://|mailto:)", literal):
                    formatted = literal
            else:
                formatted = re.sub(r"\*\*(.+?)\*\*", r"*\1*", section)
                formatted = re.sub(r"__(.+?)__", r"*\1*", formatted)
            sections.append(formatted)
        return format_links_for_slack("".join(sections))

    return "".join(
        content if fenced else format_text_section(content)
        for fenced, content in split_fenced_sections(text)
    ).strip("\r\n")


def split_fenced_sections(text: str) -> list[tuple[bool, str]]:
    """Separate literal fenced content from prose without interpreting its contents."""
    parts: list[tuple[bool, str]] = []
    section: list[str] = []
    fence_length = 0
    for line in text.strip().splitlines(keepends=True):
        fence = re.fullmatch(r"[ \t]*(`{3,})([^`]*)", line.rstrip("\r\n"))
        if fence and (
            not fence_length or (len(fence[1]) >= fence_length and not fence[2].strip())
        ):
            parts.append((bool(fence_length), "".join(section)))
            section = []
            fence_length = 0 if fence_length else len(fence[1])
        else:
            section.append(line)
    parts.append((bool(fence_length), "".join(section)))
    return parts
