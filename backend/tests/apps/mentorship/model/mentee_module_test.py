"""Tests for mentorship MenteeModule model."""

from unittest.mock import MagicMock

from apps.mentorship.models.mentee_module import MenteeModule


class TestMenteeModule:
    """Tests for MenteeModule model."""

    def test_str_returns_mentee_and_module(self):
        """Test __str__ returns formatted mentee."""
        mock = MagicMock(spec=MenteeModule)
        mock.mentee = MagicMock(__str__=lambda self: "John Doe")
        mock.module = MagicMock(__str__=lambda self: "Security Basics")

        result = MenteeModule.__str__(mock)

        assert result == "John Doe - Security Basics"
