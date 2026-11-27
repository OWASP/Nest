from unittest.mock import MagicMock

from apps.mentorship.models.program_admin import ProgramAdmin


class TestProgramAdmin:
    def test_str(self):
        """Test __str__ returns formatted admin - program (role) string."""
        mock_instance = MagicMock()
        mock_instance.admin = "John Doe"
        mock_instance.program = "GSoC 2025"
        mock_instance.role = ProgramAdmin.AdminRole.OWNER

        result = ProgramAdmin.__str__(mock_instance)

        assert result == "John Doe - GSoC 2025 (owner)"
