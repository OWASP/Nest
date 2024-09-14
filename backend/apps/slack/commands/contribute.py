"""Slack bot contribute command."""

from apps.common.utils import get_absolute_url
from apps.slack.apps import SlackConfig
from apps.slack.blocks import divider, markdown
from apps.slack.constants import OWASP_PROJECT_NEST_CHANNEL_ID


def contribute(ack, say, command):
    """Slack /contribute command handler."""
    from apps.github.models.issue import Issue
    from apps.owasp.api.search.issue import get_issues
    from apps.owasp.models.project import Project

    ack()

    # TODO(arkid15r): consider adding escaping for the user's input.
    search_query = command["text"]
    blocks = [
        divider(),
        markdown(f'*No results found for "{search_query}"*\n'),
    ]
    issues = get_issues(search_query, distinct=True, limit=10)

    if issues:
        blocks = [
            divider(),
            markdown(
                (
                    f"\n*Here are top 10 most relevant issues (1 issue per project) "
                    f"that I found for*\n `/contribute {search_query}`:\n"
                )
                if search_query
                else (
                    "\n*Here are top 10 most recent issues (1 issue per project):*\n"
                    "You can refine the results by using a more specific query, e.g.\n"
                    "`/contribute python good first issue`"
                )
            ),
        ]
        for idx, issue in enumerate(issues):
            blocks.append(
                markdown(
                    f"\n{idx + 1}. {issue['idx_project_name']}\n"
                    f"<{issue['idx_url']}|{issue['idx_title']}>\n"
                ),
            )

        blocks.append(
            markdown(
                f"⚠️ *Extended search over {Issue.open_issues_count()} open issues in "
                f"{Project.active_projects_count()} OWASP projects is available at "
                f"<{get_absolute_url('project-issues')}>*\n"
                "You can share feedback on your search experience "
                f"in the <#{OWASP_PROJECT_NEST_CHANNEL_ID}|project-nest> channel."
            ),
        )

    say(blocks=blocks)


if SlackConfig.app:
    contribute = SlackConfig.app.command("/contribute")(contribute)
