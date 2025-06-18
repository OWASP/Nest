import os
from django.test import TestCase, override_settings
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

        # Patch os.environ so real token isn't used accidentally
        self.env_patcher = patch.dict(os.environ, {"SLACK_BOT_TOKEN": "fake-token"})
        self.env_patcher.start()

        # Always return valid auth
        self.mock_web_client.auth_test.return_value = {"ok": True, "user_id": "BOT123"}

        # Create a fake workspace object in DB
        self.workspace = Workspace.objects.create(
            name="Test Workspace",
            slack_workspace_id="TEST123"
        )
        # Set up bot token in environment for the test
        os.environ["DJANGO_SLACK_BOT_TOKEN"] = "xoxb-test-token"
    def tearDown(self):
        self.app_patcher.stop()
        self.web_client_patcher.stop()

        # Patch model logic
        self.conv_update_patch = patch("apps.slack.models.Conversation.update_data", return_value=MagicMock())
        self.conv_bulk_patch = patch("apps.slack.models.Conversation.bulk_save")
        self.member_update_patch = patch("apps.slack.models.Member.update_data", return_value=MagicMock())
        self.member_bulk_patch = patch("apps.slack.models.Member.bulk_save")

        self.mock_conv_update = self.conv_update_patch.start()
        self.mock_conv_bulk = self.conv_bulk_patch.start()
        self.mock_member_update = self.member_update_patch.start()
        self.mock_member_bulk = self.member_bulk_patch.start()


        # Create Workspace (bot_token will be fetched from env, not passed)
        self.workspace = Workspace.objects.create(name="CI Test Workspace")

        # Mock Slack responses to simulate pagination and channels
        self.mock_web_client.users_list.side_effect = [
            {
                "ok": True,
                "members": [{"id": "U1"}, {"id": "U2"}],
                "response_metadata": {"next_cursor": "next-123"}
            },
            {
                "ok": True,
                "members": [{"id": "U3"}],
                "response_metadata": {"next_cursor": ""}
            }
        ]


        # Mock Slack's conversations_list response
        self.mock_web_client.conversations_list.return_value = {
            "ok": True,
            "channels": [{"id": "C1", "name": "general"}, {"id": "C2", "name": "random"}],
            "response_metadata": {"next_cursor": ""}
        }
        
        # Mock conversations.info for member count fetching
        self.mock_web_client.conversations_info.return_value = {
            "ok": True,
            "channel": {"num_members": 10}
        }

        self.mock_web_client.conversations_list.side_effect = [
            {
                "ok": True,
                "channels": [
                    {"id": "C1", "name": "general", "num_members": 5},
                    {"id": "C2", "name": "random", "num_members": 3}
                ],
                "response_metadata": {"next_cursor": ""}
            }
        ]


    def tearDown(self):
        self.app_patcher.stop()
        self.web_client_patcher.stop()
        self.env_patcher.stop()
        self.conv_update_patch.stop()
        self.conv_bulk_patch.stop()
        self.member_update_patch.stop()
        self.member_bulk_patch.stop()

    def test_command_syncs_mocked_slack_data(self):
        call_command("slack_sync_data", batch_size=100, delay=0)


        # Refresh from DB in case command saves anything
        self.workspace.refresh_from_db()

        # Verify members were created
        from apps.slack.models import Member, Conversation
        self.assertEqual(Member.objects.count(), 3)
        self.assertEqual(Conversation.objects.count(), 2)
        
        # Verify API calls were made correctly
        self.assertEqual(self.mock_web_client.users_list.call_count, 2)
        self.assertEqual(self.mock_web_client.conversations_list.call_count, 1)
        self.assertEqual(self.mock_web_client.conversations_info.call_count, 2)

        # Assertions — confirm mocks were hit
        self.assertTrue(self.mock_conv_update.called, "Conversation update was not called.")
        self.assertTrue(self.mock_conv_bulk.called, "Conversation bulk save was not called.")
        self.assertTrue(self.mock_member_update.called, "Member update was not called.")
        self.assertTrue(self.mock_member_bulk.called, "Member bulk save was not called.")

