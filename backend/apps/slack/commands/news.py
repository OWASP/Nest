"""Slack bot news command."""

from django.conf import settings

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown

COMMAND = "/news"

NEWS_ITEMS = [
    {
        "url": "https://owasp.org/blog/2024/11/26/lifecycle-events-are-part-of-the-secure-supply-chain.html",
        "title": "Lifecycle Events Are Part of the Secure Supply Chain",
        "date": "November 26, 2024",
    },
    {
        "url": "https://owasp.org/blog/2024/11/12/more-than-a-password-day-2024.html",
        "title": "More Than a Password Day 2024",
        "date": "November 12, 2024",
    },
    {
        "url": "https://owasp.org/blog/2024/10/30/owaspfoundation-org-emails.html",
        "title": "OWASP Foundation Emails Update",
        "date": "October 30, 2024",
    },
    {
        "url": "https://owasp.org/blog/2024/10/02/Securing-React-Native-Mobile-Apps-with-OWASP-MAS.html",
        "title": "Securing React Native Mobile Apps with OWASP MAS",
        "date": "October 2, 2024",
    },
    {
        "url": "https://owasp.org/blog/2024/08/01/owasp-email-problems.html",
        "title": "OWASP Email Problems and Resolution",
        "date": "August 1, 2024",
    },
    {
        "url": "https://owasp.org/blog/2024/07/09/new-coi-and-bylaws.html",
        "title": "New COI and Bylaws Announcement",
        "date": "July 9, 2024",
    },
    {
        "url": "https://owasp.org/blog/2024/07/03/asvs-community-meetup.html",
        "title": "ASVS Community Meetup Recap",
        "date": "July 3, 2024",
    },
    {
        "url": "https://owasp.org/blog/2024/05/30/secureflag-threatcanvas-member-benefit.html",
        "title": "SecureFlag ThreatCanvas Member Benefit",
        "date": "May 30, 2024",
    },
    {
        "url": "https://owasp.org/blog/2024/04/22/starr-brown-hired-as-director-projects.html",
        "title": "Starr Brown Hired as Director of Projects",
        "date": "April 22, 2024",
    },
    {
        "url": "https://owasp.org/blog/2024/04/18/codebashing-member-benefit.html",
        "title": "Codebashing Member Benefit Announcement",
        "date": "April 18, 2024",
    },
]


def news_handler(ack, command, client):
    """Slack /news command handler."""
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    blocks = [
        markdown("*:newspaper: Here are the latest OWASP news:*"),
    ]
    for idx, item in enumerate(NEWS_ITEMS[:10], start=1):
        blocks.append(markdown(f"*{idx}. {item['title']}*"))
        blocks.append(markdown(f"Published on: *{item['date']}*"))
        blocks.append(markdown(f"<{item['url']}|Read more>"))
    blocks.append(
        markdown(
            f"{NL}For more news, please visit the <https://owasp.org/news/|OWASP News Page>{NL}"
        )
    )

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    news_handler = SlackConfig.app.command(COMMAND)(news_handler)
