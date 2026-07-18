"""Channel router service for NestBot.

Routes OWASP-related messages to the most relevant Slack channel
instead of always running the full RAG pipeline.
"""

from __future__ import annotations

from apps.slack.constants import (
    OWASP_APPSEC_CHANNEL_ID,
    OWASP_ASKOWASP_CHANNEL_ID,
    OWASP_CONTRIBUTE_CHANNEL_ID,
    OWASP_DEVSECOPS_CHANNEL_ID,
    OWASP_GSOC_CHANNEL_ID,
    OWASP_JOBS_CHANNEL_ID,
    OWASP_MENTORS_CHANNEL_ID,
    OWASP_PROJECT_JUICE_SHOP_CHANNEL_ID,
    OWASP_PROJECT_NEST_CHANNEL_ID,
    OWASP_PROJECT_NETTACKER_CHANNEL_ID,
    OWASP_PROJECT_THREAT_DRAGON_CHANNEL_ID,
    OWASP_SPONSORSHIP_CHANNEL_ID,
    OWASP_THREAT_MODELING_CHANNEL_ID,
)

PROJECT_CHANNEL_MAP: list[tuple[frozenset[str], str, str]] = [
    (
        frozenset({"juice shop", "juiceshop", "webgoat"}),
        OWASP_PROJECT_JUICE_SHOP_CHANNEL_ID,
        "project-juice-shop",
    ),
    (frozenset({"nettacker"}), OWASP_PROJECT_NETTACKER_CHANNEL_ID, "project-nettacker"),
    (
        frozenset({"threat dragon", "threatdragon"}),
        OWASP_PROJECT_THREAT_DRAGON_CHANNEL_ID,
        "project-threat-dragon",
    ),
    (frozenset({"nest", "nestbot"}), OWASP_PROJECT_NEST_CHANNEL_ID, "project-nest"),
    (
        frozenset({"gsoc", "google summer of code", "summer of code"}),
        OWASP_GSOC_CHANNEL_ID,
        "gsoc",
    ),
    (
        frozenset({"contribute", "contributing", "contribution", "how to contribute"}),
        OWASP_CONTRIBUTE_CHANNEL_ID,
        "contribute",
    ),
    (
        frozenset(
            {"job", "jobs", "hiring", "career", "careers", "position", "vacancy"}
        ),
        OWASP_JOBS_CHANNEL_ID,
        "jobs",
    ),
    (
        frozenset({"mentor", "mentorship", "mentoring"}),
        OWASP_MENTORS_CHANNEL_ID,
        "mentors",
    ),
    (
        frozenset({"sponsor", "sponsorship", "sponsoring", "donate", "donation"}),
        OWASP_SPONSORSHIP_CHANNEL_ID,
        "sponsorship",
    ),
    (
        frozenset(
            {"threat model", "threat modeling", "threat modelling", "stride", "pasta"}
        ),
        OWASP_THREAT_MODELING_CHANNEL_ID,
        "threat-modeling",
    ),
    (
        frozenset({"devsecops", "devsec", "dev sec ops"}),
        OWASP_DEVSECOPS_CHANNEL_ID,
        "devsecops",
    ),
    (
        frozenset({"appsec", "application security", "top 10", "top10", "owasp top"}),
        OWASP_APPSEC_CHANNEL_ID,
        "appsec",
    ),
    (
        frozenset({"chapter", "local chapter", "owasp chapter"}),
        OWASP_ASKOWASP_CHANNEL_ID,
        "ask-owasp",
    ),
]


def route(message: str) -> tuple[str, str] | None:
    """Return the most relevant channel for the given message, or None.

    Args:
        message (str): The user's Slack message text.

    Returns:
        tuple[str, str] | None: (channel_id, label) if a match is found,
        or None if the question is general and should go through RAG.

    """
    if not message:
        return None

    lower = message.lower()
    for keywords, channel_id, label in PROJECT_CHANNEL_MAP:
        if any(kw in lower for kw in keywords):
            return channel_id, label

    return None
