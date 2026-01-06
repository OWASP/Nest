from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest


class MockIntegrityError(Exception):
    pass

from apps.mentorship.models import Program, Mentor
from apps.github.models import User as GithubUser


class TestProgram:
    
    def test_program_status_choices(self):
        assert Program.ProgramStatus.DRAFT == "draft"
        assert Program.ProgramStatus.PUBLISHED == "published"
        assert Program.ProgramStatus.COMPLETED == "completed"

    def test_str_returns_name(self):
        mock_program_instance = Program(name="Security Program")
        assert Program.__str__(mock_program_instance) == "Security Program"