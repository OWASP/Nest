from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.common.constants import OWASP_URL
from apps.owasp.utils.staff import get_staff_data
from apps.slack.commands.staff import Staff

FAILED_STAFF_DATA_ERROR_MESSAGE = "Failed to get OWASP Foundation staff data."


class TestStaffHandler:
    @pytest.fixture
    def mock_slack_command(self):
        return {
            "user_id": "U123456",
        }

    @pytest.fixture
    def mock_slack_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.fixture
    def mock_staff(self):
        return [
            {
                "description": "Daily operations and team management",
                "location": "WA, USA",
                "name": "Jane Smith",
                "title": "Operations Manager",
            },
            {
                "description": "Leadership and strategic direction",
                "location": "CA, USA",
                "name": "John Doe",
                "title": "Executive Director",
            },
        ]

    @pytest.mark.parametrize(
        ("commands_enabled", "has_staff_data", "expected_message"),
        [
            (False, True, None),
            (True, True, "OWASP Foundation Staff:"),
            (True, False, FAILED_STAFF_DATA_ERROR_MESSAGE),
        ],
    )
    def test_handler_responses(
        self,
        commands_enabled,
        has_staff_data,
        expected_message,
        mock_slack_client,
        mock_slack_command,
        mock_staff,
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        # Clear cache before test
        get_staff_data.cache_clear()
        # Patch where it's imported and used
        with patch("apps.slack.commands.staff.get_staff_data") as mock_get_staff_data:
            mock_get_staff_data.return_value = mock_staff if has_staff_data else None

            ack = MagicMock()
            Staff().handler(ack=ack, command=mock_slack_command, client=mock_slack_client)

            ack.assert_called_once()

            if not commands_enabled:
                mock_slack_client.conversations_open.assert_not_called()
                mock_slack_client.chat_postMessage.assert_not_called()
            elif has_staff_data:
                mock_slack_client.conversations_open.assert_called_once_with(
                    users=mock_slack_command["user_id"]
                )
                blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
                # Combine all text blocks to check content
                all_text = "\n".join(
                    block["text"]["text"] for block in blocks if "text" in block.get("text", {})
                )
                assert expected_message in all_text
                for idx, staff in enumerate(mock_staff, start=1):
                    assert f"*{idx}. {staff['name']}, {staff['title']}*" in all_text
                    assert f"_{staff['location']}_" in all_text
                    assert staff["description"] in all_text
                # Check that the footer is present
                assert OWASP_URL in all_text
                # Check that the feedback message is present
                assert "💬 You can share feedback" in all_text
            else:
                mock_slack_client.conversations_open.assert_called_once_with(
                    users=mock_slack_command["user_id"]
                )
                mock_slack_client.chat_postMessage.assert_called_once()
                blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
                all_text = "\n".join(
                    block["text"]["text"] for block in blocks if "text" in block.get("text", {})
                )
                assert FAILED_STAFF_DATA_ERROR_MESSAGE in all_text
