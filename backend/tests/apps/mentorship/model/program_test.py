from unittest.mock import MagicMock, patch

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

    @patch("apps.common.models.TimestampedModel.save")
    def test_save_sets_key_from_name(self, mock_super_save):
        """Test save method sets key from slugified name."""
        mock_program = MagicMock(spec=Program)
        mock_program.name = "My Test Program"

        Program.save(mock_program)

        assert mock_program.key is not None
        mock_super_save.assert_called_once()
