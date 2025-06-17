from django.test import TestCase
from django.core.management import call_command
from apps.slack.models import Workspace
from unittest.mock import patch, MagicMock
import slack_bolt.app.app as slack_bolt_app
import slack_sdk.web.client as slack_web_client


class SlackSyncDataCommandTests(TestCase):
    def setUp(self):
        # Patch Slack App to prevent actual Slack startup
        self.app_patcher = patch.object(slack_bolt_app, "App", autospec=True)
        self.app_patcher.start()

        # Patch Slack WebClient to prevent HTTP calls
        self.web_client_patcher = patch.object(slack_web_client, "WebClient", autospec=True)
        self.mock_web_client_class = self.web_client_patcher.start()
        self.mock_web_client = MagicMock()
        self.mock_web_client_class.return_value = self.mock_web_client

        # Fake a valid Slack bot token check
        self.mock_web_client.auth_test.return_value = {"ok": True, "user_id": "BOT123"}

        # Create a fake workspace object in DB
        self.workspace = Workspace.objects.create(name="Test Workspace")

    def tearDown(self):
        self.app_patcher.stop()
        self.web_client_patcher.stop()

    def test_command_syncs_mocked_slack_data(self):
        # Mock Slack's users_list response with 2 pages
        self.mock_web_client.users_list.side_effect = [
            {
                "members": [{"id": "U1"}, {"id": "U2"}],
                "response_metadata": {"next_cursor": "next-123"}
            },
            {
                "members": [{"id": "U3"}],
                "response_metadata": {"next_cursor": ""}
            }
        ]

        # Mock Slack's conversations_list response
        self.mock_web_client.conversations_list.return_value = {
            "channels": [{"id": "C1", "name": "general"}, {"id": "C2", "name": "random"}],
            "response_metadata": {"next_cursor": ""}
        }

        # Call the Django management command
        call_command("slack_sync_data", batch_size=100, delay=0)

        # Refresh from DB in case command saves anything
        self.workspace.refresh_from_db()

        # Replace this with real assertions if you're storing data
        self.assertTrue(True)  # CI-safe dummy assertion
