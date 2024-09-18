"""Slack bot contribute command."""

from django.conf import settings
from django.utils.text import Truncator

from apps.common.utils import get_absolute_url
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE
from apps.slack.utils import escape

COMMAND = "/contribute"
TEXT_TRUNCATION_LIMIT = 260


def handler(ack, say, command):
    """Slack /contribute command handler."""
    from apps.github.models.issue import Issue
    from apps.owasp.api.search.issue import get_issues

    ack()
    if not settings.SLACK_COMMANDS_ENABLED:
        return

    search_query = command["text"]
    search_query_escaped = escape(command["text"])
    blocks = [
        markdown(f"*No results found for `{COMMAND} {search_query_escaped}`*\n"),
    ]

    if issues := get_issues(search_query, distinct=True, limit=10):
        blocks = [
            markdown(
                (
                    f"\n*Here are top 10 most relevant issues (1 issue per project) "
                    f"that I found for*\n `{COMMAND} {search_query_escaped}`:\n"
                )
                if search_query_escaped
                else (
                    "\n*Here are top 10 most recent issues (1 issue per project):*\n"
                    "You can refine the results by using a more specific query, e.g. "
                    f"`{COMMAND} python good first issue`"
                )
            ),
        ]

        for idx, issue in enumerate(issues):
            summary_truncated = Truncator(issue["idx_summary"]).chars(
                TEXT_TRUNCATION_LIMIT, truncate="..."
            )
            blocks.append(
                markdown(
                    f"\n*{idx + 1}. {escape(issue['idx_project_name'])}*\n"
                    f"<{issue['idx_url']}|{escape(issue['idx_title'])}>\n"
                    f"{escape(summary_truncated)}\n"
                ),
            )

        blocks.append(
            markdown(
                f"⚠️ *Extended search over {Issue.open_issues_count()} open issues "
                f"is available at <{get_absolute_url('project-issues')}|{settings.SITE_NAME}>*\n"
                f"{FEEDBACK_CHANNEL_MESSAGE}"
            ),
        )

    say(blocks=blocks)


if SlackConfig.app:
    handler = SlackConfig.app.command(COMMAND)(handler)
