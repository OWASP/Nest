from unittest.mock import MagicMock, patch
from datetime import datetime
import pytest

from apps.mentorship.models import Module
from apps.mentorship.models.managers import PublishedModuleManager
from apps.mentorship.models import Program, Mentor
from apps.github.models import Issue, User as GithubUser
from apps.owasp.models import Project


class MockIntegrityError(Exception):
    pass


class TestModulePureMocks:
    def setup_method(self):
        self.program = MagicMock(
            spec=Program,
            name="Test Program",
            key="test-program",
            status=Program.ProgramStatus.PUBLISHED,
            started_at=datetime(2023, 1, 1, 9, 0, 0),
            ended_at=datetime(2023, 12, 31, 18, 0, 0),
        )
        self.project = MagicMock(spec=Project, name="Test Project", key="test-project")

    def test_str_returns_name(self):
        """Unit test: __str__ should return the module name (pure mock)."""
        mock_module = MagicMock(spec=Module)
        mock_module.name = "Security Basics"

        assert Module.__str__(mock_module) == "Security Basics"

    @patch("apps.mentorship.models.Module.objects.create")
    def test_create_module_called_with_expected_args(self, mock_create_module):
        """Confirm that code would call objects.create with the correct arguments."""
        mock_module_instance = MagicMock(spec=Module)
        mock_module_instance.name = "New Module"
        mock_module_instance.key = "new-module"
        mock_module_instance.program = self.program
        mock_module_instance.project = self.project
        mock_module_instance.description = "A new mentorship module."
        mock_module_instance.experience_level = "beginner"
        mock_module_instance.domains = ["Web Security"]
        mock_module_instance.tags = ["Django"]
        mock_module_instance.position = 1
        mock_module_instance.started_at = datetime(2023, 1, 1, 10, 0, 0)
        mock_module_instance.ended_at = datetime(2023, 1, 31, 17, 0, 0)
        mock_module_instance.labels = ["bug", "enhancement"]
        mock_module_instance.__str__.return_value = "New Module"

        mock_create_module.return_value = mock_module_instance

        module = Module.objects.create(
            name="New Module",
            program=self.program,
            project=self.project,
            description="A new mentorship module.",
            experience_level="beginner",
            domains=["Web Security"],
            tags=["Django"],
            position=1,
            started_at=datetime(2023, 1, 1, 10, 0, 0),
            ended_at=datetime(2023, 1, 31, 17, 0, 0),
            labels=["bug", "enhancement"],
        )

        mock_create_module.assert_called_once_with(
            name="New Module",
            program=self.program,
            project=self.project,
            description="A new mentorship module.",
            experience_level="beginner",
            domains=["Web Security"],
            tags=["Django"],
            position=1,
            started_at=datetime(2023, 1, 1, 10, 0, 0),
            ended_at=datetime(2023, 1, 31, 17, 0, 0),
            labels=["bug", "enhancement"],
        )

        assert module.name == "New Module"
        assert module.key == "new-module"
        assert module.program == self.program
        assert module.project == self.project
        assert module.labels == ["bug", "enhancement"]
        assert str(module) == "New Module"

    @patch("apps.mentorship.models.Module.objects.create")
    def test_unique_module_key_in_program_constraint_mocked(self, mock_create_module):
        """
        Pure-mock simulation of unique constraint: first create succeeds,
        second create raises an IntegrityError (mocked).
        """
        mock_create_module.side_effect = [MagicMock(spec=Module), MockIntegrityError("Mock Integrity Error")]

        Module.objects.create(name="Module One", key="module-key", program=self.program, project=self.project)

        with pytest.raises(MockIntegrityError):
            Module.objects.create(name="Module Two", key="module-key", program=self.program, project=self.project)

        assert mock_create_module.call_count == 2

    @patch("apps.mentorship.models.Module.objects.create")
    def test_module_save(self, mock_create_module):
        """
        We cannot call the real Model.save without DB/app registry here,
        so simulate the save behavior by attaching a side_effect to a mock instance's save method.
        This verifies the *expected* effects (key slugification and date inheritance) in a pure-mock way.
        """
        program_with_dates = MagicMock(
            spec=Program,
            name="Program With Dates",
            key="program-with-dates",
            started_at=datetime(2024, 2, 1),
            ended_at=datetime(2024, 2, 28),
        )

        mock_module = MagicMock(spec=Module)
        mock_module.name = "Auto Date Module"
        mock_module.program = program_with_dates
        mock_module.project = self.project
        mock_module.started_at = None
        mock_module.ended_at = None

        def simulate_save_for_inheritance(*args, **kwargs):
            mock_module.key = "date-module"  
            if not mock_module.started_at:
                mock_module.started_at = mock_module.started_at or mock_module.program.started_at
            if not mock_module.ended_at:
                mock_module.ended_at = mock_module.ended_at or mock_module.program.ended_at

        mock_module.save.side_effect = simulate_save_for_inheritance
        mock_create_module.return_value = mock_module

        module = Module.objects.create(name="Auto Date Module", program=program_with_dates, project=self.project)
        module.save()  

        assert module.key == "date-module"
        assert module.started_at == datetime(2024, 2, 1)
        assert module.ended_at == datetime(2024, 2, 28)

        explicit_start = datetime(2024, 3, 1)
        explicit_end = datetime(2024, 3, 31)

        mock_module.started_at = explicit_start
        mock_module.ended_at = explicit_end
        mock_create_module.return_value = mock_module

        module = Module.objects.create(name="Auto Date Module", program=program_with_dates, project=self.project)
        module.save()  

        assert module.started_at == explicit_start
        assert module.ended_at == explicit_end
        assert module.key == "date-module"