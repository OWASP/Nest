"""Slack bot user joined #contribute channel handler."""

from django.conf import settings

from apps.common.utils import get_absolute_url
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.constants import (
    FEEDBACK_CHANNEL_MESSAGE,
    NEST_BOT_NAME,
    OWASP_CONTRIBUTE_CHANNEL_ID,
)


def handler(event, client, ack):
    """Slack #contribute new user handler."""
    from apps.github.models.issue import Issue
    from apps.owasp.models.project import Project

    ack()

    if not settings.SLACK_EVENTS_ENABLED or event["channel"] != OWASP_CONTRIBUTE_CHANNEL_ID:
        return

    user_id = event["user"]
    conversation = client.conversations_open(users=user_id)

    client.chat_postMessage(
        channel=conversation["channel"]["id"],
        blocks=[
            markdown(
                f"Hello <@{user_id}> and welcome to <#{OWASP_CONTRIBUTE_CHANNEL_ID}> channel!\n"
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
                "With `/contribute` command you can easily find options for contributing right "
                "here in this chat. It's a quick and convenient way to get involved! "
                "Alternatively, you can check out "
                f"<{get_absolute_url('project-issues')}|*{settings.SITE_NAME}*> where you'll find "
                "a comprehensive list of projects and ways to make a difference. It also offers "
                "guidance on possible first steps to approach the issues within OWASP projects."
            ),
            markdown(f"{FEEDBACK_CHANNEL_MESSAGE}"),
        ],
    )


if SlackConfig.app:
    handler = SlackConfig.app.event("member_joined_channel")(handler)
