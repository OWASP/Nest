"""Fuzz target for apps.slack.common.text."""

import sys

import atheris

with atheris.instrument_imports():
    from apps.slack.common.text import escape, format_links_for_slack, strip_markdown


def test_one_input(data: bytes) -> None:
    """Fuzz Slack formatting utilities with arbitrary Unicode input."""
    text = data.decode("utf-8", errors="surrogateescape")
    escape(text)
    format_links_for_slack(text)
    strip_markdown(text)

    fdp = atheris.FuzzedDataProvider(data)
    structured_text = fdp.ConsumeUnicodeNoSurrogates(512)
    escape(structured_text)
    format_links_for_slack(structured_text)
    strip_markdown(structured_text)


def main() -> None:
    """Run the Atheris fuzz target."""
    atheris.Setup(sys.argv, atheris.instrument_func(test_one_input))
    atheris.Fuzz()


if __name__ == "__main__":
    main()
