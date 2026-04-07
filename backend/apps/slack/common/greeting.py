"""Simple greeting / thanks detection — no agent for pure social messages."""

from __future__ import annotations

import re

_QUESTION_MARK = re.compile(r"\?")
# Substantive question: interrogatives, common auxiliaries before a clause, or imperatives.
_SUBSTANTIVE_QUESTION = re.compile(
    r"\b("
    r"what|when|where|who|whom|whose|why|how|which|"
    r"can\s+you|could\s+you|would\s+you|should\s+you|will\s+you|"
    r"do\s+you|does|did|is\s+there|are\s+there|is\s+it|are\s+we|"
    r"explain|describe|define|list|compare|recommend|how\s+do\s+i|how\s+to|"
    r"tell\s+me|show\s+me|help\s+me"
    r")\b",
    re.IGNORECASE,
)

_THANKS_ONLY = re.compile(
    r"^(thanks|thank\s+you|thx|ty|cheers|much\s+appreciated)"
    r"(\s*[!,.])?(\s+again|\s+so\s+much)?\s*$",
    re.IGNORECASE,
)

_GREETING_ONLY = re.compile(
    r"^(hi|hello|hey|howdy|greetings|yo|sup)\b"
    r"(\s*[!,.])?(\s+there|\s+team|\s+all|\s+everyone|\s+bot|\s+nestbot)?\s*$",
    re.IGNORECASE,
)

_GOOD_DAY = re.compile(
    r"^good\s+(morning|afternoon|evening|day|night)\b\s*[!,.]?\s*$",
    re.IGNORECASE,
)

_MAX_GREETING_LEN = 200

_REPLY_THANKS = (
    "You're welcome! If you have OWASP or application security questions, ask anytime."
)
_REPLY_GOOD_DAY = (
    "Hello! When you're ready, ask me about OWASP or application security."
)
_REPLY_HELLO = (
    "Hi! I'm NestBot — ask me about OWASP and application security whenever you like."
)


def _clean_for_match(text: str) -> str:
    """Drop Slack user/channel mentions and collapse whitespace."""
    without_mentions = re.sub(r"<@[^>]+>", " ", text)
    without_mentions = re.sub(r"<#[^|]+\|[^>]+>", " ", without_mentions)
    return " ".join(without_mentions.split()).strip()


def has_substantive_question(text: str) -> bool:
    """Return whether the text likely contains a question for the agent."""
    cleaned = _clean_for_match(text)
    if not cleaned:
        return False
    if _QUESTION_MARK.search(cleaned):
        return True
    return bool(_SUBSTANTIVE_QUESTION.search(cleaned))


def is_simple_greeting(text: str) -> bool:
    """Return whether text is a short hello/thanks with no substantive question."""
    cleaned = _clean_for_match(text)
    if not cleaned or len(cleaned) > _MAX_GREETING_LEN:
        return False
    if has_substantive_question(cleaned):
        return False
    return bool(
        _THANKS_ONLY.match(cleaned)
        or _GREETING_ONLY.match(cleaned)
        or _GOOD_DAY.match(cleaned)
    )


def canned_greeting_reply(text: str) -> str | None:
    """Return a fixed friendly reply, or None to route the message to the agent."""
    if not is_simple_greeting(text):
        return None
    cleaned = _clean_for_match(text)
    if _THANKS_ONLY.match(cleaned):
        return _REPLY_THANKS
    if _GOOD_DAY.match(cleaned):
        return _REPLY_GOOD_DAY
    return _REPLY_HELLO
