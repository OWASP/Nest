"""Slack bot user joined team handler using templates."""

import logging

from slack_sdk.errors import SlackApiError

from apps.common.constants import OWASP_NEST_URL
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
    OWASP_SPONSORSHIP_CHANNEL_ID,
    OWASP_THREAT_MODELING_CHANNEL_ID,
)
from apps.slack.events.event import EventBase
from apps.slack.utils import get_text

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
            "appsec_channel": OWASP_APPSEC_CHANNEL_ID,
            "ask_channel": OWASP_ASKOWASP_CHANNEL_ID,
            "community_channel": OWASP_COMMUNITY_CHANNEL_ID,
            "contribute_channel": OWASP_CONTRIBUTE_CHANNEL_ID,
            "developers_channel": OWASP_DEVELOPERS_CHANNEL_ID,
            "devsecops_channel": OWASP_DEVSECOPS_CHANNEL_ID,
            "FEEDBACK_CHANNEL_MESSAGE": FEEDBACK_CHANNEL_MESSAGE,
            "gsoc_channel": OWASP_GSOC_CHANNEL_ID,
            "jobs_channel": OWASP_JOBS_CHANNEL_ID,
            "juice_shop_channel": OWASP_PROJECT_JUICE_SHOP_CHANNEL_ID,
            "leaders_channel": OWASP_LEADERS_CHANNEL_ID,
            "london_channel": OWASP_CHAPTER_LONDON_CHANNEL_ID,
            "mentors_channel": OWASP_MENTORS_CHANNEL_ID,
            "nest_url": OWASP_NEST_URL,
            "project_nest_channel": OWASP_PROJECT_NEST_CHANNEL_ID,
            "sponsorship_channel": OWASP_SPONSORSHIP_CHANNEL_ID,
            "threat_modeling_channel": OWASP_THREAT_MODELING_CHANNEL_ID,
            "user_id": event["user"]["id"],
        }

    def handle_event(self, event, client):
        """Handle the team_join event."""
        user_id = event["user"]["id"]  # User object is returned (other events return just the ID)!

        try:
            conversation = self.open_conversation(client, user_id)
            blocks = self.get_render_blocks(self.get_context(event))
            client.chat_postMessage(
                blocks=blocks,
                channel=conversation["channel"]["id"],
                text=get_text(blocks),
            )
        except SlackApiError as e:
            if e.response["error"] == "cannot_dm_bot":
                logger.warning("Cannot DM bot user %s", user_id)
                return
            logger.exception("Slack API error in team_join handler: %s", e.response["error"])
            raise
        except Exception:
            logger.exception("Error in team_join handler for user: %s", user_id)
            raise
