"""Tests for canned greeting replies (no agent)."""

import pytest

from apps.slack.common.greeting import canned_greeting_reply


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
def test_canned_greeting_positive(text):
    assert canned_greeting_reply(text) is not None


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
def test_canned_greeting_negative(text):
    assert canned_greeting_reply(text) is None


def test_greeting_with_user_mention_stripped():
    assert canned_greeting_reply("<@U123> hi") is not None
    assert canned_greeting_reply("<@U123> what is OWASP") is None


def test_canned_greeting_reply_variants():
    assert "welcome" in (canned_greeting_reply("Thanks") or "").lower()
    assert canned_greeting_reply("Good afternoon") is not None
    assert canned_greeting_reply("What is XSS?") is None


def test_question_words_route_to_agent():
    assert canned_greeting_reply("Hi how does XSS work") is None
