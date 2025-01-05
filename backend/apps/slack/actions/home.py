"""Slack home actions handler."""

import logging

from slack_sdk.errors import SlackApiError

from apps.slack.apps import SlackConfig
from apps.slack.constants import NL

logger = logging.getLogger(__name__)


def handle_home_actions(ack, body, client):
    """Handle actions triggered in the Slack Home Tab."""
    from apps.owasp.api.search.chapter import get_chapters
    from apps.owasp.api.search.committee import get_committees
    from apps.owasp.api.search.project import get_projects

    ack()

    action_id = body["actions"][0]["action_id"]
    user_id = body["user"]["id"]

    try:
        if action_id == "view_projects_action":
            project_details = get_projects(query="", limit=10, page=1)
            view_title = "*Projects*"
            blocks = []

            if project_details["hits"]:
                content = (
                    f"Here are the top {len(project_details['hits'])} projects you can explore:\n"
                )
                for project in project_details["hits"]:
                    project_card = {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": (
                                f"*<{project['idx_url']}|{project['idx_name']}>*{NL}"
                                f":bust_in_silhouette: *Contributors:* "
                                f"{project['idx_contributors_count']}"
                                f" :fork_and_knife: *Forks:* {project['idx_forks_count']}"
                                f" :star2: *Stars:* {project['idx_stars_count']}\n"
                            ),
                        },
                    }
                    blocks.append(project_card)

            else:
                content = "No projects found based on your search query."
                blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": content}})

        elif action_id == "view_committees_action":
            committee_details = get_committees(query="", limit=10, page=1)
            view_title = "*Committees*"
            blocks = []

            if committee_details["hits"]:
                content = (
                    f"Here are the top {len(committee_details['hits'])} committees you can join:\n"
                )
                for committee in committee_details["hits"]:
                    committee_card = {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": (
                                f"*<{committee['idx_url']}|{committee['idx_name']}>*\n"
                                f"{committee['idx_summary']}\n"
                            ),
                        },
                    }
                    blocks.append(committee_card)

            else:
                content = "No committees found based on your search query."
                blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": content}})

        elif action_id == "view_chapters_action":
            chapter_details = get_chapters(query="", limit=10, page=1)
            view_title = "*Chapters*"
            blocks = []

            if chapter_details["hits"]:
                content = f"Here are the top {len(chapter_details['hits'])} chapters"
                "you can be a part of:\n"
                for chapter in chapter_details["hits"]:
                    chapter_card = {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": (
                                f"*<{chapter['idx_url']}|{chapter['idx_name']}>*\n"
                                f"{chapter['idx_summary']}\n"
                            ),
                        },
                    }
                    blocks.append(chapter_card)

            else:
                content = "No chapters found based on your search query."
                blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": content}})

        else:
            view_title = "*Unknown Action*"
            content = "Invalid action, please try again."

        new_home_view = {
            "type": "home",
            "blocks": [
                {"type": "section", "text": {"type": "mrkdwn", "text": view_title}},
                *blocks,
            ],
        }

        client.views_publish(user_id=user_id, view=new_home_view)

    except SlackApiError as e:
        logger.exception("Error publishing Home Tab for user %s: %s", user_id, e.response["error"])


if SlackConfig.app:
    SlackConfig.app.action("view_chapters_action")(handle_home_actions)
    SlackConfig.app.action("view_committees_action")(handle_home_actions)
    SlackConfig.app.action("view_projects_action")(handle_home_actions)
