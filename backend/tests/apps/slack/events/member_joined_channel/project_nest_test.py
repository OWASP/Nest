"""Tests for ProjectNest member joined channel event handler."""

from pathlib import Path

from apps.slack.events.member_joined_channel.project_nest import ProjectNest


class TestProjectNest:
    """Test cases for ProjectNest event handler."""

    def test_direct_message_template_path_returns_none(self):
        """Test that direct_message_template_path returns None."""
        handler = ProjectNest()

        assert handler.direct_message_template_path is None

    def test_ephemeral_message_template_path(self):
        """Test that ephemeral_message_template_path returns correct path."""
        handler = ProjectNest()

        result = handler.ephemeral_message_template_path

        assert isinstance(result, Path)
        assert str(result) == "events/member_joined_channel/project_nest/ephemeral_message.jinja"
