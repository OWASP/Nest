"""Tests for mentorship MenteeProgram model."""

from unittest.mock import MagicMock

from apps.mentorship.models.mentee_program import MenteeProgram


class TestMenteeProgram:
    """Tests for MenteeProgram model."""

    def test_str_returns_mentee_and_program(self):
        """Test __str__ returns formatted mentee."""
        mock = MagicMock(spec=MenteeProgram)
        mock.mentee = MagicMock(__str__=lambda _: "Jane Doe")
        mock.program = MagicMock(__str__=lambda _: "Security Program")

        result = MenteeProgram.__str__(mock)

        assert result == "Jane Doe - Security Program"
