"""Slack bot chapters command."""

from django.conf import settings

from apps.common.constants import NL
from apps.common.utils import get_absolute_url
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.commands.constants import COMMAND_HELP, COMMAND_START
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE
from apps.slack.utils import escape

COMMAND = "/chapters"


def handler(ack, command, client):
    """Slack /chapters command handler."""
    from apps.owasp.api.search.chapter import get_chapters
    from apps.owasp.models.chapter import Chapter

    ack()
    if not settings.SLACK_COMMANDS_ENABLED:
        return

    command_text = command["text"].strip()

    if command_text in COMMAND_HELP:
        blocks = [
            markdown(
                f"*Available Commands:*{NL}"
                f"• `/chapters` - recent chapters{NL}"
                f"• `/chapters [search term]` - Search for specific chapters{NL}"
                f"• `/chapters [region]` - Search for specific region chapters{NL}"
            ),
        ]
    else:
        search_query = "" if command_text in COMMAND_START else command_text
        search_query_escaped = escape(search_query)
        blocks = [
            markdown(f"*No results found for `{COMMAND} {search_query_escaped}`*{NL}"),
        ]

        attributes = [
            "idx_leaders",
            "idx_name",
            "idx_suggested_location",
            "idx_summary",
            "idx_region",
            "idx_country",
            "idx_updated_at",
            "idx_url",
        ]

        if chapters := get_chapters(search_query, attributes=attributes, limit=10)["hits"]:
            blocks = [
                markdown(
                    f"{NL}*OWASP chapters that I found for* `{search_query_escaped}` query:{NL}"
                    if search_query_escaped
                    else f"{NL}*OWASP chapters:*{NL}"
                ),
            ]

            for idx, chapter in enumerate(chapters):
                location = chapter["idx_suggested_location"] or chapter["idx_country"]
                leaders = chapter.get("idx_leaders", [])
                leaders = (
                    f"_Leader{'' if len(leaders) == 1 else 's'}: {', '.join(leaders)}_{NL}"
                    if leaders
                    else ""
                )
                blocks.append(
                    markdown(
                        f"{idx + 1}. <{chapter['idx_url']}|*{chapter['idx_name']}*>{NL}"
                        f"_{location}_{NL}"
                        f"{leaders}"
                        f"{escape(chapter['idx_summary'])}{NL}"
                    )
                )

            blocks.append(
                markdown(
                    f"⚠️ *Extended search over {Chapter.active_chapters_count()} OWASP chapters "
                    f"is available at <{get_absolute_url('chapters')}"
                    f"?q={search_query}|{settings.SITE_NAME}>*{NL}"
                    f"{FEEDBACK_CHANNEL_MESSAGE}"
                ),
            )

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    handler = SlackConfig.app.command(COMMAND)(handler)
