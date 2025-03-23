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
            workspace_id = workspace.slack_workspace_id
            workspace_name = workspace.name or "Unnamed"
            bot_token = workspace.bot_token

            self.stdout.write(f"\nProcessing workspace: {workspace_name} ({workspace_id})")

            if not bot_token:
                self.stdout.write(self.style.ERROR(f"No bot token found for {workspace_id}"))
                continue

            # Slack client
            client = WebClient(token=bot_token)

            # populate channels
            self.stdout.write(f"Fetching channels for {workspace_id}...")
            try:
                response = client.conversations_list(
                    types="public_channel,private_channel", limit=1000
                )
                self._handle_slack_response(response, "conversations_list")

                for channel in response["channels"]:
                    Channel.objects.update_or_create(
                        workspace=workspace,
                        slack_channel_id=channel["id"],
                        defaults={
                            "name": channel["name"],
                            "is_private": channel["is_private"],
                            "member_count": channel.get("num_members", 0),
                        },
                    )
                self.stdout.write(
                    self.style.SUCCESS(f"Populated {len(response['channels'])} channels")
                )
            except SlackApiError as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to fetch channels: {e.response['error']}")
                )

            # populate members
            self.stdout.write(f"Fetching members for {workspace_id}...")
            try:
                response = client.users_list(limit=1000)
                self._handle_slack_response(response, "users_list")

                member_count = 0
                for user in response["members"]:
                    if not user["is_bot"] and user["id"] != "USLACKBOT":
                        Member.objects.update_or_create(
                            workspace=workspace,
                            slack_user_id=user["id"],
                            defaults={
                                "username": user["name"],
                                "real_name": user.get("real_name", ""),
                                "email": user["profile"].get("email", "Not available"),
                            },
                        )
                        member_count += 1
                self.stdout.write(self.style.SUCCESS(f"Populated {member_count} members"))
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
