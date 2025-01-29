from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.common.constants import OWASP_WEBSITE_URL
from apps.slack.commands.events import events_handler


class TestEventsHandler:
    @pytest.fixture()
    def mock_slack_command(self):
        return {
            "user_id": "U123456",
        }

    @pytest.fixture()
    def mock_slack_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.fixture()
    def mock_events(self):
        return [
            {
                "category": "Global",
                "description": "Our premier events bring together our communities.",
                "events": [
                    {
                        "name": "OWASP Global AppSec EU 2025",
                        "start-date": date(2025, 5, 26),
                        "dates": "May 26-30, 2025",
                        "url": "https://example.com/eu2025",
                    },
                    {
                        "name": "OWASP Global AppSec US 2025",
                        "start-date": date(2025, 11, 3),
                        "dates": "November 3-7, 2025",
                    },
                ],
            },
            {
                "category": "AppSec Days",
                "description": "Local OWASP volunteers organize conferences.",
                "events": [
                    {
                        "name": "OWASP Snow 2025",
                        "start-date": date(2025, 3, 14),
                        "dates": "March 14, 2025",
                        "url": "https://example.com/snowfroc",
                        "optional-text": "Premier application security conference",
                    },
                ],
            },
        ]

    @pytest.mark.parametrize(
        ("commands_enabled", "has_events_data", "expected_header"),
        [
            (False, True, None),
            (True, True, "*Upcoming OWASP Events: *"),
            (True, False, "*Upcoming OWASP Events: *"),
        ],
    )
    @patch("apps.slack.commands.events.get_events_data")
    def test_handler_responses(
        self,
        mock_get_events_data,
        commands_enabled,
        has_events_data,
        expected_header,
        mock_slack_client,
        mock_slack_command,
        mock_events,
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        mock_get_events_data.return_value = mock_events if has_events_data else []

        events_handler(
            ack=MagicMock(), command=mock_slack_command, client=mock_slack_client
        )

        if not commands_enabled:
            mock_slack_client.conversations_open.assert_not_called()
            mock_slack_client.chat_postMessage.assert_not_called()
            return

        # Verify basic message structure
        mock_slack_client.conversations_open.assert_called_once_with(
            users=mock_slack_command["user_id"]
        )

        blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]

        # Check header
        assert blocks[0]["text"]["text"] == expected_header

        if has_events_data:
            current_block = 2  # Skip header and divider
            
            # Check each category
            for category_data in mock_events:
                # Verify category header
                category_block = blocks[current_block]["text"]["text"]
                assert f"*{category_data['category']} Events:*" in category_block
                assert category_data["description"] in category_block
                current_block += 1

                # Verify events in category
                sorted_events = sorted(
                    category_data["events"],
                    key=lambda x: x["start-date"],
                )
                
                for idx, event in enumerate(sorted_events, 1):
                    event_block = blocks[current_block]["text"]["text"]
                    
                    # Check basic event info
                    assert f"*{idx}. {event['name']}*" in event_block
                    assert f"{event['dates']}" in event_block
                    
                    # Check optional fields
                    if event.get("url"):
                        assert f"🔗 <{event['url']}|More Information>" in event_block
                    if event.get("optional-text"):
                        assert f"_{event['optional-text']}_" in event_block
                    
                    current_block += 1
                
                current_block += 1  # Skip divider

            # Verify footer
            footer_block = blocks[-1]["text"]["text"]
            assert "🔍 For more information about upcoming events" in footer_block
            assert OWASP_WEBSITE_URL in footer_block

    def test_format_event_block(self):
        """Test the format_event_block function independently."""
        from apps.slack.commands.events import format_event_block

        # Test with minimal event data
        minimal_event = {
            "name": "Test Event",
            "dates": "Jan 1, 2025",
        }
        result = format_event_block(minimal_event, 1)
        assert "Test Event" in result["text"]["text"]
        assert "Jan 1, 2025" in result["text"]["text"]
        assert "More Information" not in result["text"]["text"]
        assert "_" not in result["text"]["text"]

        # Test with full event data
        full_event = {
            "name": "Test Event",
            "dates": "Jan 1, 2025",
            "url": "https://example.com",
            "optional-text": "Additional information",
        }
        result = format_event_block(full_event, 1)
        assert "Test Event" in result["text"]["text"]
        assert "Jan 1, 2025" in result["text"]["text"]
        assert "https://example.com" in result["text"]["text"]
        assert "Additional information" in result["text"]["text"]
        
        