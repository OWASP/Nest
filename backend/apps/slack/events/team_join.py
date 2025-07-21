"""Slack bot user joined team handler using templates."""

import logging

from apps.slack.constants import (
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
    OWASP_SPONSORSHIP_CHANNEL_ID,
    OWASP_THREAT_MODELING_CHANNEL_ID,
)
from apps.slack.events.event import EventBase

logger: logging.Logger = logging.getLogger(__name__)


class TeamJoin(EventBase):
    """Slack bot user joined team event handler."""

    event_type = "team_join"

    def get_context(self, event):
        """Get the template context.

        Args:
            event: The Slack event

        Returns:
            dict: The template context.

        """
        return {
            **super().get_context(event),
            "APPSEC_CHANNEL_ID": OWASP_APPSEC_CHANNEL_ID,
            "ASKOWASP_CHANNEL_ID": OWASP_ASKOWASP_CHANNEL_ID,
            "COMMUNITY_CHANNEL_ID": OWASP_COMMUNITY_CHANNEL_ID,
            "CONTRIBUTE_CHANNEL_ID": OWASP_CONTRIBUTE_CHANNEL_ID,
            "DEVELOPERS_CHANNEL_ID": OWASP_DEVELOPERS_CHANNEL_ID,
            "DEVSECOPS_CHANNEL_ID": OWASP_DEVSECOPS_CHANNEL_ID,
            "GSOC_CHANNEL_ID": OWASP_GSOC_CHANNEL_ID,
            "JOBS_CHANNEL_ID": OWASP_JOBS_CHANNEL_ID,
            "LEADERS_CHANNEL_ID": OWASP_LEADERS_CHANNEL_ID,
            "LONDON_CHAPTER_CHANNEL_ID": OWASP_CHAPTER_LONDON_CHANNEL_ID,
            "MENTORS_CHANNEL_ID": OWASP_MENTORS_CHANNEL_ID,
            "PROJECT_JUICE_SHOP_CHANNEL_ID": OWASP_PROJECT_JUICE_SHOP_CHANNEL_ID,
            "PROJECT_NEST_CHANNEL_ID": OWASP_PROJECT_NEST_CHANNEL_ID,
            "SPONSORSHIP_CHANNEL_ID": OWASP_SPONSORSHIP_CHANNEL_ID,
            "THREAT_MODELING_CHANNEL_ID": OWASP_THREAT_MODELING_CHANNEL_ID,
        }

    def get_user_id(self, event):
        """Get the user ID from the event.

        Args:
            event: The Slack event

        Returns:
            str: The user ID.

        """
        return event["user"]["id"]  # User object is returned (other events return just the ID)!
