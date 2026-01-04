import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from apps.mentorship.models import Mentee, MenteeProgram, Program
from apps.github.models import User as GithubUser


class MockIntegrityError(Exception):
    pass


class TestMenteeProgram:
    def setup_method(self):
        self.github_user = MagicMock(spec=GithubUser, login="testmentee")
        self.mentee = MagicMock(
            spec=Mentee,
            github_user=self.github_user,
            __str__=lambda self: "testmentee",
        )
        self.program = MagicMock(
            spec=Program,
            name="Test Program",
            key="test-program",
            __str__=lambda self: "Test Program",
        )

    @patch("apps.mentorship.models.MenteeProgram.objects.create")
    def test_create_mentee_program(self, mock_create):
        start_time = datetime(2023, 1, 1, 10, 0, 0)
        end_time = datetime(2023, 1, 1, 11, 0, 0)

        mock_mentee_program_instance = MagicMock(spec=MenteeProgram)
        mock_mentee_program_instance.mentee = self.mentee
        mock_mentee_program_instance.program = self.program
        mock_mentee_program_instance.started_at = start_time
        mock_mentee_program_instance.ended_at = end_time
        mock_mentee_program_instance.experience_level = "beginner"
        mock_mentee_program_instance.__str__.return_value = f"{self.mentee} - {self.program}"

        mock_create.return_value = mock_mentee_program_instance

        mentee_program = MenteeProgram.objects.create(
            mentee=self.mentee,
            program=self.program,
            started_at=start_time,
            ended_at=end_time,
            experience_level="beginner",
        )

        mock_create.assert_called_once_with(
            mentee=self.mentee,
            program=self.program,
            started_at=start_time,
            ended_at=end_time,
            experience_level="beginner",
        )
        assert mentee_program.mentee == self.mentee
        assert mentee_program.program == self.program
        assert mentee_program.started_at == start_time
        assert mentee_program.ended_at == end_time
        assert mentee_program.experience_level == "beginner"
        assert str(mentee_program) == f"{self.mentee} - {self.program}"

    @patch("apps.mentorship.models.MenteeProgram.objects.create")
    def test_unique_together_constraint(self, mock_create):
        mock_create.side_effect = [
            MagicMock(spec=MenteeProgram),
            MockIntegrityError("Mock Integrity Error"),
        ]

        MenteeProgram.objects.create(
            mentee=self.mentee,
            program=self.program,
            started_at=datetime(2023, 1, 1, 10, 0, 0),
        )

        with pytest.raises(MockIntegrityError):
            MenteeProgram.objects.create(
                mentee=self.mentee,
                program=self.program,
                started_at=datetime(2023, 1, 1, 10, 0, 0),
            )

        assert mock_create.call_count == 2
