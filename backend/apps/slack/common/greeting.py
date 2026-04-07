"""Canned replies for short greetings; skips the AI agent."""

import re

_MAX_LEN = 200

_THANKS = re.compile(
    r"^(thanks|thank\s+you|thx|ty|cheers|much\s+appreciated)(\s*[!,.])?(\s+again|\s+so\s+much)?\s*$",
    re.IGNORECASE,
)
_GREETING = re.compile(
    r"^(hi|hello|hey|howdy|greetings)(\s*[!,.])?(\s+there|\s+team|\s+all|\s+everyone|\s+bot|\s+nestbot)?\s*$",
    re.IGNORECASE,
)
_GOOD_DAY = re.compile(
    r"^good\s+(morning|afternoon|evening|day|night)\b\s*[!,.]?\s*$",
    re.IGNORECASE,
)
_QUESTIONISH = re.compile(
    r"\?|\b(what|when|where|who|whom|why|how|which|explain|define|describe|"
    r"tell\s+me|show\s+me|help\s+me|how\s+to|how\s+do\s+i)\b",
    re.IGNORECASE,
)

_REPLY_THANKS = (
    "You're welcome! If you have OWASP or application security questions, ask anytime."
)
_REPLY_GOOD_DAY = (
    "Hello! When you're ready, ask me about OWASP or application security."
)
_REPLY_HELLO = (
    "Hi! I'm NestBot — ask me about OWASP and application security whenever you like."
)


def _clean(text: str) -> str:
    return " ".join(re.sub(r"<@[^>]+>", " ", text).split()).strip()


def canned_greeting_reply(text: str) -> str | None:
    """Return a fixed reply for hello/thanks-only text, or None to use the agent."""
    cleaned = _clean(text)
    if not cleaned or len(cleaned) > _MAX_LEN or _QUESTIONISH.search(cleaned):
        return None
    if _THANKS.match(cleaned):
        return _REPLY_THANKS
    if _GOOD_DAY.match(cleaned):
        return _REPLY_GOOD_DAY
    if _GREETING.match(cleaned):
        return _REPLY_HELLO
    return None
