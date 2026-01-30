from unittest.mock import MagicMock

from apps.mentorship.models import Program


class TestProgram:
    def test_program_status_choices(self):
        assert Program.ProgramStatus.DRAFT == "draft"
        assert Program.ProgramStatus.PUBLISHED == "published"
        assert Program.ProgramStatus.COMPLETED == "completed"

    def test_str_returns_name(self):
        mock_program_instance = MagicMock(spec=Program)
        mock_program_instance.name = "Security Program"
        assert Program.__str__(mock_program_instance) == "Security Program"
