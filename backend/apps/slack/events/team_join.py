"""Slack bot user joined team handler."""

import logging

from django.conf import settings
from slack_sdk.errors import SlackApiError

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.constants import (
    FEEDBACK_CHANNEL_MESSAGE,
    OWASP_APPSEC_CHANNEL_ID,
    OWASP_ASKOWASP_CHANNEL_ID,
    OWASP_CHAPTER_LONDON_CHANNEL_ID,
    OWASP_COMMUNITY_CHANNEL_ID,
    OWASP_CONTRIBUTE_CHANNEL_ID,
    OWASP_DEVELOPERS_CHANNEL_ID,
    OWASP_DEVSECOPS_CHANNEL_ID,
    OWASP_GSOC_CHANNEL_ID,
    OWASP_JOBS_CHANNEL_ID,
    OWASP_LEADERS_CHANNEL_ID,
    OWASP_MENTORS_CHANNEL_ID,
    OWASP_PROJECT_JUICE_SHOP_CHANNEL_ID,
    OWASP_PROJECT_NEST_CHANNEL_ID,
    OWASP_THREAT_MODELING_CHANNEL_ID,
)
from apps.slack.utils import get_text

logger = logging.getLogger(__name__)


def team_join_handler(event, client, ack):
    """Slack new team user handler."""
    ack()
    if not settings.SLACK_EVENTS_ENABLED:
        return

    user_id = event["user"]["id"]  # User object is returned -- other events return just the ID!
    try:
        conversation = client.conversations_open(users=user_id)
    except SlackApiError as e:
        if e.response["error"] == "cannot_dm_bot":
            logger.warning("Error opening conversation with bot user %s", user_id)
            return
        logger.exception(client.users_info(user=user_id))
        raise

    blocks = [
        markdown(
            f"*Welcome to the OWASP Slack Community, <@{user_id}>!*{NL}"
            "We're excited to have you join us! Whether you're a newcomer to OWASP or "
            "a seasoned contributor, this is the space to connect, collaborate, "
            f"and learn together!{2*NL}"
        ),
        markdown(
            f"*Get Started*:{NL}"
            "To explore the full spectrum of OWASP's projects, chapters, and resources, "
            "check out <https://nest.owasp.org|*OWASP Nest*>. It's your gateway to "
            "discovering ways to contribute, stay informed, and connect with the OWASP "
            "community. From finding projects aligned with your interests to engaging with "
            "chapters in your area, OWASP Nest makes it easier to navigate and get involved."
        ),
        markdown(
            f"*Connect and Grow:*{NL}"
            f"  • Visit OWASP channels <{OWASP_COMMUNITY_CHANNEL_ID}> and "
            f"<{OWASP_ASKOWASP_CHANNEL_ID}> to engage with the broader community.{2*NL}"
            f"  • Find your local chapter channel (normally chapter specific channels have "
            f"`#chapter-<name>` format, e.g. <{OWASP_CHAPTER_LONDON_CHANNEL_ID}>){2*NL}"
            f"  • Dive into project-specific channels, like `#project-<name>` (e.g. "
            f"<{OWASP_PROJECT_JUICE_SHOP_CHANNEL_ID}>, <{OWASP_PROJECT_NEST_CHANNEL_ID}>) "
            f"to engage directly with the project specific communities.{2*NL}"
            f"  • Explore topic channels like <{OWASP_APPSEC_CHANNEL_ID}>, "
            f"<{OWASP_DEVSECOPS_CHANNEL_ID}>, <{OWASP_THREAT_MODELING_CHANNEL_ID}> to "
            f"engage with like-minded individuals.{2*NL}"
            f"  • Join <{OWASP_JOBS_CHANNEL_ID}> to discover job opportunities in the cyber "
            f"security field."
        ),
        markdown(
            f"*Learn and Engage:*{NL}"
            f"  • Explore <{OWASP_CONTRIBUTE_CHANNEL_ID}> for opportunities to get involved "
            f"in OWASP projects and initiatives.{2*NL}"
            f"  • Join leadership channels: <{OWASP_LEADERS_CHANNEL_ID}> and "
            f"<{OWASP_MENTORS_CHANNEL_ID}> to connect with OWASP leaders and mentors.{2*NL}"
            f"  • Learn about OWASP's participation in Google Summer of Code in "
            f"<{OWASP_GSOC_CHANNEL_ID}>.{2*NL}"
            f"  • Connect with developers in <{OWASP_DEVELOPERS_CHANNEL_ID}> to discuss "
            f"development practices and tools."
        ),
        markdown(
            "We're here to support your journey in making software security visible and "
            "strengthening the security of the software we all depend on. Have questions or "
            "need help? Don't hesitate to ask—this community thrives on collaboration!"
        ),
        markdown(f"{FEEDBACK_CHANNEL_MESSAGE}"),
    ]

    client.chat_postMessage(
        blocks=blocks,
        channel=conversation["channel"]["id"],
        text=get_text(blocks),
    )


if SlackConfig.app:
    team_join_handler = SlackConfig.app.event("team_join")(team_join_handler)
