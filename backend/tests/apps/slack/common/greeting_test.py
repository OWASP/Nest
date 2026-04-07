"""Tests for simple greeting detection (no agent)."""

import pytest

from apps.slack.common.greeting import (
    canned_greeting_reply,
    has_substantive_question,
    is_simple_greeting,
)


@pytest.mark.parametrize(
    "text",
    [
        "Hi",
        "Hello",
        "Hey there",
        "Thanks",
        "Thank you!",
        "Good morning",
        "thx",
    ],
)
def test_is_simple_greeting_positive(text):
    assert is_simple_greeting(text)


@pytest.mark.parametrize(
    "text",
    [
        "Hi, what is OWASP?",
        "Thanks — can you explain XSS?",
        "Hello? Is anyone there?",
        "What is SQL injection",
        "How do I fix CSRF",
        "Tell me about the Top 10",
        "",
        "x" * 300,
    ],
)
def test_is_simple_greeting_negative(text):
    assert not is_simple_greeting(text)


def test_greeting_with_mention_stripped():
    assert is_simple_greeting("<@U123> hi")
    assert not is_simple_greeting("<@U123> what is OWASP")


def test_canned_greeting_reply_variants():
    assert "welcome" in (canned_greeting_reply("Thanks") or "").lower()
    assert canned_greeting_reply("Hi") is not None
    assert canned_greeting_reply("Good afternoon") is not None
    assert canned_greeting_reply("What is XSS?") is None


def test_has_substantive_question():
    assert has_substantive_question("What is OWASP?")
    assert has_substantive_question("Hi how does XSS work")
    assert not has_substantive_question("Hello")
