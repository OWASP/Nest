import logging
from django.conf import settings
from slack_sdk.errors import SlackApiError
from slack_sdk.models.views import View
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown

logger = logging.getLogger(__name__)


def handler(event, client, ack):
    """Handles the app_home_opened event to update the Slack Home Tab."""
    ack()

    if not settings.SLACK_EVENTS_ENABLED:
        return

    user_id = event["user"]

    try:
        # Define the Home Tab view
        home_view = {
            "type": "home",
            "blocks": [
                markdown(
                    "*Quick Actions:*"
                ),
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "🌟 View Projects",
                                "emoji": True
                            },
                            "value": "view_projects",
                            "action_id": "view_projects_action"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "👥 View Committees",
                                "emoji": True
                            },
                            "value": "view_committees",
                            "action_id": "view_committees_action"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📚 View Chapters",
                                "emoji": True
                            },
                            "value": "view_chapters",
                            "action_id": "view_chapters_action"
                        }
                    ]
                },
                markdown(
                    f"""*🏠 Welcome to NestBot, <@{user_id}>!* 
                    """
                ),
            ]
        }

        client.views_publish(user_id=user_id, view=home_view)
        logger.info(f"Home tab updated for user {user_id}")

    except SlackApiError as e:
        logger.error(
            f"Error publishing Home Tab for user {user_id}: {e.response['error']}")


if SlackConfig.app:
    # Register the app home opened event handler
    SlackConfig.app.event("app_home_opened")(handler)
