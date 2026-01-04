from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest


class MockIntegrityError(Exception):
    pass

from apps.mentorship.models import Program, Mentor
from apps.github.models import User as GithubUser


class TestProgram:
    def setup_method(self):
        self.mentor_github_user = MagicMock(spec=GithubUser, login="adminuser", github_id=999)
        self.mentor = MagicMock(spec=Mentor, github_user=self.mentor_github_user, __str__=lambda self: "adminuser")

    def test_create_program(self):
        mock_program_instance = MagicMock(spec=Program)
        mock_program_instance.name = "New Program"
        mock_program_instance.key = "new-program"
        mock_program_instance.description = "A new mentorship program."
        mock_program_instance.started_at = datetime(2023, 1, 1, 10, 0, 0)
        mock_program_instance.ended_at = datetime(2023, 12, 31, 17, 0, 0)
        mock_program_instance.status = Program.ProgramStatus.PUBLISHED
        mock_program_instance.experience_levels = ["beginner", "intermediate"]
        mock_program_instance.domains = ["AppSec"]
        mock_program_instance.tags = ["Python"]
        mock_program_instance.mentees_limit = 10
        mock_program_instance.__str__.return_value = "New Program"

        with patch("apps.mentorship.models.Program.objects.create", return_value=mock_program_instance) as mock_create_program:
            program = Program.objects.create(
                name="New Program",
                description="A new mentorship program.",
                started_at=datetime(2023, 1, 1, 10, 0, 0),
                ended_at=datetime(2023, 12, 31, 17, 0, 0),
                status=Program.ProgramStatus.PUBLISHED,
                experience_levels=["beginner", "intermediate"],
                domains=["AppSec"],
                tags=["Python"],
                mentees_limit=10,
            )
            mock_create_program.assert_called_once_with(
                name="New Program",
                description="A new mentorship program.",
                started_at=datetime(2023, 1, 1, 10, 0, 0),
                ended_at=datetime(2023, 12, 31, 17, 0, 0),
                status=Program.ProgramStatus.PUBLISHED,
                experience_levels=["beginner", "intermediate"],
                domains=["AppSec"],
                tags=["Python"],
                mentees_limit=10,
            )
            assert program.name == "New Program"
            assert program.key == "new-program"
            assert program.description == "A new mentorship program."
            assert program.started_at == datetime(2023, 1, 1, 10, 0, 0)
            assert program.ended_at == datetime(2023, 12, 31, 17, 0, 0)
            assert program.status == Program.ProgramStatus.PUBLISHED
            assert program.experience_levels == ["beginner", "intermediate"]
            assert program.domains == ["AppSec"]
            assert program.tags == ["Python"]
            assert program.mentees_limit == 10
            assert str(program) == "New Program"

    def test_program_status_choices(self):
        assert Program.ProgramStatus.DRAFT == "draft"
        assert Program.ProgramStatus.PUBLISHED == "published"
        assert Program.ProgramStatus.COMPLETED == "completed"

    def test_str_returns_name(self):
        mock_program_instance = Program(name="Security Program")
        assert Program.__str__(mock_program_instance) == "Security Program"