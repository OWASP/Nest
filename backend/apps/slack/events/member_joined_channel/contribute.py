"""Slack member joined #contribute channel handler."""

import logging

from django.conf import settings
from slack_sdk.errors import SlackApiError

from apps.common.constants import NL
from apps.common.utils import get_absolute_url
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.common.gsoc import GSOC_2025_MILESTONES
from apps.slack.constants import (
    FEEDBACK_CHANNEL_MESSAGE,
    NEST_BOT_NAME,
    OWASP_CONTRIBUTE_CHANNEL_ID,
)
from apps.slack.utils import get_text

logger = logging.getLogger(__name__)


def contribute_handler(event, client, ack):
    """Slack #contribute new member handler."""
    from apps.github.models.issue import Issue
    from apps.owasp.models.project import Project

    ack()
    if not settings.SLACK_EVENTS_ENABLED:
        return

    user_id = event["user"]

    try:
        conversation = client.conversations_open(users=user_id)
    except SlackApiError as e:
        if e.response["error"] == "cannot_dm_bot":
            logger.warning("Error opening conversation with bot user %s", user_id)
            return
        raise

    client.chat_postEphemeral(
        blocks=GSOC_2025_MILESTONES,
        channel=event["channel"],
        text=get_text(GSOC_2025_MILESTONES),
        user=user_id,
    )

    blocks = [
        markdown(
            f"Hello <@{user_id}> and welcome to <{OWASP_CONTRIBUTE_CHANNEL_ID}> channel!{NL}"
            "We're happy to have you here as part of the OWASP community! "
            "Your eagerness to contribute is what makes our community strong. "
            f"With *{Project.active_projects_count()} active OWASP projects*, there are "
            "countless opportunities for you to get involved and make a meaningful impact."
        ),
        markdown(
            f"Currently, we have *{Issue.open_issues_count()} recently opened issues* across "
            "these projects, and your skills and insights could help us tackle them. Whether "
            "you're interested in coding, documentation, testing, or community outreach, "
            "there's a place for you here. Don't hesitate to jump in, ask questions, and "
            "share your ideas. Together, we can enhance the state of application security!"
        ),
        markdown(
            f"{NEST_BOT_NAME} can help you jumpstart your contributions to OWASP projects. "
            "You can easily find opportunities for contributing right here in this chat using "
            "`/contribute --start` command. It's a quick and convenient way to get involved! "
            "Alternatively, you can check out "
            f"<{get_absolute_url('projects/contribute')}|*OWASP Nest Issues*> where you'll "
            "find a comprehensive list of OWASP contribution opportunities and ways to make a "
            "difference. It also offers guidance on possible first steps to approach the "
            "issues within OWASP projects."
        ),
        markdown(
            "🎉 We're excited to have you on board, and we can't wait to see the amazing "
            "contributions you'll make! "
        ),
        markdown(f"{FEEDBACK_CHANNEL_MESSAGE}"),
    ]
    client.chat_postMessage(
        blocks=blocks,
        channel=conversation["channel"]["id"],
        text=get_text(blocks),
    )


if SlackConfig.app:
    SlackConfig.app.event(
        "member_joined_channel",
        matchers=[lambda event: f"#{event['channel']}" == OWASP_CONTRIBUTE_CHANNEL_ID],
    )(contribute_handler)
