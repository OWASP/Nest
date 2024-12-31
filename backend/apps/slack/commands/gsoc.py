from django.conf import settings
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.commands.constants import COMMAND_START
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE, NL


COMMAND = "/gsoc"
VALID_YEARS = range(2020, 2025)

def get_gsoc_projects_by_year(year):
    """Get GSOC projects for a specific year using search."""
    from apps.owasp.api.search.project import get_projects
    query = f'gsoc{year}'
    print(f"query ",query)
    return get_projects(
        query=query,
        attributes=['idx_name', 'idx_summary', 'idx_url', 'idx_type', 'idx_level'],
        limit=100
    )

def handler(ack, command, client):
    """Slack /gsoc command handler."""
    from apps.slack.common.gsoc import GSOC_GENERAL_INFORMATION_BLOCKS
    ack()
    if not settings.SLACK_COMMANDS_ENABLED:
        return
   
    command_text = command["text"].strip()
    print(f"command ",command)
    if not command_text or command_text in COMMAND_START:
        blocks = [
            *GSOC_GENERAL_INFORMATION_BLOCKS,
            markdown(f"{FEEDBACK_CHANNEL_MESSAGE}"),
        ]
    else:
        try:
            year = int(command_text)
            print(f"year ",year)
            if year in VALID_YEARS:
                results = get_gsoc_projects_by_year(year)
                if results['hits']:
                    blocks = []
                    for hit in results['hits']:
                        blocks.extend([
                            markdown(f"*{hit['idx_name']}*\n"
                                   f"{hit['idx_summary']}\n"
                                   f"Type: {hit['idx_type']} | Level: {hit['idx_level']}\n"
                                   f"URL: {hit['idx_url']}")
                        ])
                else:
                    blocks = [markdown(f"No projects found for GSOC {year}")]
            else:
                blocks = [markdown("Usage: `/gsoc [year]`\nValid years: 2020-2024")]
        except ValueError:
            blocks = [markdown("Usage: `/gsoc [year]`\nValid years: 2020-2024")]

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)

if SlackConfig.app:
    handler = SlackConfig.app.command(COMMAND)(handler)