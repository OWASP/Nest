"""A command to populate Slack channels and members data based on workspaces's bot tokens."""

from django.core.management.base import BaseCommand
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from apps.slack.models import Channel, Member, Workspace


class Command(BaseCommand):
    help = "Populate channels and members for all Slack workspaces using their bot tokens"

    def handle(self, *args, **options):
        workspaces = Workspace.objects.all()

        if not workspaces:
            self.stdout.write(self.style.WARNING("No workspaces found in the database"))
            return

        for workspace in workspaces:
            self.stdout.write(f"\nProcessing workspace: {workspace}")

            if not (bot_token := workspace.bot_token):
                self.stdout.write(self.style.ERROR(f"No bot token found for {workspace}"))
                continue

            # Slack client
            client = WebClient(token=bot_token)

            # Populate channels
            self.stdout.write(f"Fetching channels for {workspace}...")
            total_channels = 0
            try:
                cursor = None
                while True:
                    response = client.conversations_list(
                        types="public_channel,private_channel", limit=1000, cursor=cursor
                    )
                    self._handle_slack_response(response, "conversations_list")

                    for channel in response["channels"]:
                        Channel.update_data(workspace, channel)
                    total_channels += len(response["channels"])

                    cursor = response.get("response_metadata", {}).get("next_cursor")
                    if not cursor:
                        break

                self.stdout.write(self.style.SUCCESS(f"Populated {total_channels} channels"))
            except SlackApiError as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to fetch channels: {e.response['error']}")
                )

            self.stdout.write(f"Fetching members for {workspace}...")
            total_members = 0
            try:
                cursor = None
                while True:
                    response = client.users_list(limit=1000, cursor=cursor)
                    self._handle_slack_response(response, "users_list")

                    member_count = 0
                    for member in response["members"]:
                        if not member["is_bot"] and member["id"] != "USLACKBOT":
                            Member.update_data(workspace, member)
                            member_count += 1
                    total_members += member_count

                    cursor = response.get("response_metadata", {}).get("next_cursor")
                    if not cursor:
                        break

                self.stdout.write(self.style.SUCCESS(f"Populated {total_members} members"))
            except SlackApiError as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to fetch members: {e.response['error']}")
                )

        self.stdout.write(self.style.SUCCESS("\nFinished processing all workspaces"))

    def _handle_slack_response(self, response, api_method):
        """Handle Slack API response and raise exception if needed."""
        if not response["ok"]:
            error_message = f"{api_method} API call failed"
            raise SlackApiError(error_message, response)
