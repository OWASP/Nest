from unittest.mock import Mock

from apps.slack.events.reaction_added import ReactionAdded


class TestReactionAdded:
    def test_handle_event_delegates_to_moderation_service(self, mocker):
        """Test reaction_added events delegate moderation processing to the service."""
        service = mocker.patch("apps.slack.events.reaction_added.process_reaction_added")
        event = {"type": "reaction_added"}
        client = Mock()

        ReactionAdded().handle_event(event, client)

        service.assert_called_once_with(event, client)
