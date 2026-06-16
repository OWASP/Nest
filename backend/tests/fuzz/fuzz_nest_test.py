"""OWASP Nest fuzz target for ClusterFuzzLite.

escape(), format_links_for_slack(), and strip_markdown() from
apps/slack/utils/format.py are reproduced inline because
apps/slack/__init__.py imports slack_sdk which is unavailable in the
ClusterFuzzLite build environment. The functions are self-contained
string utilities with no external dependencies.
"""

import re
import sys
from html import escape as escape_html

import atheris


def escape(content: str) -> str:
    """Escape HTML special characters."""
    return escape_html(content, quote=False)


def format_links_for_slack(text: str) -> str:
    """Convert Markdown links to Slack link format."""
    if not text:
        return text
    return re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)").sub(r"<\2|\1>", text)


def strip_markdown(text: str) -> str:
    """Strip Slack markdown formatting."""
    return re.compile(r"<(https?://[^|]+)\|([^>]+)>").sub(r"\2 (\1)", text).replace("*", "")


def test_one_input(data: bytes) -> None:
    """Fuzz Slack formatting utilities with arbitrary Unicode input."""
    fdp = atheris.FuzzedDataProvider(data)
    text = fdp.ConsumeUnicodeNoSurrogates(512)

    escape(text)
    format_links_for_slack(text)
    strip_markdown(text)


def main() -> None:
    """Run the Atheris fuzz target."""
    atheris.Setup(sys.argv, atheris.instrument_func(test_one_input))
    atheris.Fuzz()


if __name__ == "__main__":
    main()
