"""Slack bot news command."""

from urllib.parse import urljoin

import requests
from django.conf import settings
from django.core.cache import cache
from lxml import html

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown

COMMAND = "/news"
NEWS_URL = "https://owasp.org/news/"
CACHE_TIMEOUT = 600  # Cache for 10 minutes
SUCCESS_RESPONSE = 200


def fetch_latest_news():
    """Fetch the 10 latest news from OWASP using lxml, with caching."""
    cache_key = "owasp_latest_news"
    cached_news = cache.get(cache_key)

    if cached_news:
        return cached_news  # Return cached data if available

    response = requests.get(NEWS_URL, timeout=10)
    if response.status_code != SUCCESS_RESPONSE:
        return []

    tree = html.fromstring(response.content)
    news_items = []

    h2_tags = tree.xpath("//h2")

    for h2 in h2_tags[:11]:
        anchor = h2.xpath(".//a[@href]")

        if anchor:
            title = anchor[0].text_content().strip()
            relative_url = anchor[0].get("href")
            full_url = urljoin(NEWS_URL, relative_url)

            author_tag = h2.xpath("./following-sibling::p[@class='author']")
            author = author_tag[0].text_content().strip() if author_tag else "Unknown"

            news_items.append(
                {
                    "url": full_url,
                    "title": title,
                    "author": author,
                }
            )

    cache.set(cache_key, news_items, CACHE_TIMEOUT)

    return news_items


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
