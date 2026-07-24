from apps.slack.models.conversation import Conversation
from apps.slack.models.reaction_rule import ReactionRule
from apps.slack.models.workspace import Workspace


class TestReactionRule:
    def test_str(self):
        """Test reaction rule string includes conversation and emoji."""
        workspace = Workspace(name="OWASP")
        conversation = Conversation(name="general", workspace=workspace)
        rule = ReactionRule(conversation=conversation, emoji_name="spam")

        assert str(rule) == "OWASP #general :spam"
