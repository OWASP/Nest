from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings
from requests.exceptions import RequestException

from apps.slack.commands.staff import staff_handler
from apps.slack.constants import OWASP_WEBSITE_URL


class TestStaffHandler:
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
    def mock_staff(self):
        return [
            {
                "name": "John Doe",
                "title": "Executive Director",
                "description": "Leadership and strategic direction",
            },
            {
                "name": "Jane Smith",
                "title": "Operations Manager",
                "description": "Daily operations and team management",
            },
        ]

    @pytest.mark.parametrize(
        ("commands_enabled", "has_staff_data", "expected_message"),
        [
            (False, True, None),
            (True, True, "Here are the OWASP staff members:"),
            (True, False, "Failed to get staff data."),
        ],
    )
    @patch("apps.slack.commands.staff.get_staff_data")
    def test_handler_responses(
        self,
        mock_get_staff,
        commands_enabled,
        has_staff_data,
        expected_message,
        mock_slack_client,
        mock_slack_command,
        mock_staff,
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled

        if has_staff_data:
            mock_get_staff.return_value = mock_staff
        else:
            mock_get_staff.side_effect = RequestException

        staff_handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        if not commands_enabled:
            mock_slack_client.conversations_open.assert_not_called()
            mock_slack_client.chat_postMessage.assert_not_called()
        elif has_staff_data:
            mock_slack_client.conversations_open.assert_called_once_with(
                users=mock_slack_command["user_id"]
            )
            blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
            assert blocks[0]["text"]["text"] == expected_message
            for idx, staff in enumerate(mock_staff, start=1):
                staff_block = blocks[idx]["text"]["text"]
                assert f"*{idx}.* *Name:* *{staff['name']}*" in staff_block
                assert f"*Title:* _{staff['title']}_" in staff_block
                assert f"*Description:* {staff['description']}" in staff_block
            assert OWASP_WEBSITE_URL in blocks[-1]["text"]["text"]
        else:
            mock_slack_client.chat_postMessage.assert_called_once_with(
                channel=mock_slack_command["user_id"], text="Failed to get staff data."
            )
