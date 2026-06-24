from apps.slack.models.conversation import Conversation
from apps.slack.models.moderation import ModerationRule
from apps.slack.models.workspace import Workspace


class TestModerationRule:
    def test_str(self):
        """Test moderation rule string includes conversation and emoji."""
        workspace = Workspace(name="OWASP")
        conversation = Conversation(name="general", workspace=workspace)
        rule = ModerationRule(conversation=conversation, emoji_name="spam")

        assert str(rule) == "OWASP #general :spam"
