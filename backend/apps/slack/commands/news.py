"""Slack bot news command."""

from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from django.conf import settings

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown

COMMAND = "/news"
NEWS_URL = "https://owasp.org/news/"


def fetch_latest_news():
    """Fetch the 10 latest news from OWASP using BeautifulSoup."""
    response = requests.get(NEWS_URL, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")

    news_items = []

    h2_tags = soup.find_all("h2")

    for h2 in h2_tags:
        anchor = h2.find("a", href=True)

        if anchor:
            title = anchor.get_text(strip=True)
            relative_url = anchor["href"]
            full_url = urljoin(NEWS_URL, relative_url)

            author_tag = h2.find_next("p", class_="author")
            author = author_tag.get_text(strip=True) if author_tag else "Unknown"

            news_items.append(
                {
                    "url": full_url,
                    "title": title,
                    "author": author,
                }
            )

    return news_items[:10]


def news_handler(ack, command, client):
    """Slack /news command handler."""
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    news_items = fetch_latest_news()
    if not news_items:
        blocks = [markdown(":warning: *Failed to fetch OWASP news. Please try again later.*")]
    else:
        blocks = [markdown("*:newspaper: Here are the latest OWASP news:*")]
        for idx, item in enumerate(news_items, start=1):
            blocks.append(markdown(f"*{idx}. {item['title']}* - <{item['url']}|Read more> :link:"))
            blocks.append(markdown(f"*:memo: Published by:* {item['author']}"))
            blocks.append(markdown("-" * 40))

        blocks.append(
            markdown(
                f"{NL}For more, visit <{NEWS_URL}|OWASP News Page> :globe_with_meridians:{NL}"
            )
        )

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    news_handler = SlackConfig.app.command(COMMAND)(news_handler)
