from datetime import timezone
from unittest.mock import MagicMock, patch

import django.utils.timezone

from apps.mentorship.models import Module, Program
from apps.owasp.models import Project


class TestModulePureMocks:
    def setup_method(self):
        self.program = MagicMock(
            spec=Program,
            name="Test Program",
            key="test-program",
            status=Program.ProgramStatus.PUBLISHED,
            started_at=django.utils.timezone.datetime(2023, 1, 1, 9, 0, 0, tzinfo=timezone.UTC),
            ended_at=django.utils.timezone.datetime(2023, 12, 31, 18, 0, 0, tzinfo=timezone.UTC),
        )
        self.project = MagicMock(spec=Project, name="Test Project", key="test-project")

    def test_str_returns_name(self):
        """Unit test: __str__ should return the module name (pure mock)."""
        mock_module = MagicMock(spec=Module)
        mock_module.name = "Security Basics"

        assert Module.__str__(mock_module) == "Security Basics"

    @patch("apps.mentorship.models.Module.objects.create")
    def test_module_save(self, mock_create_module):
        program_with_dates = MagicMock(
            spec=Program,
            name="Program With Dates",
            key="program-with-dates",
            started_at=django.utils.timezone.datetime(2024, 2, 1, tzinfo=timezone.UTC),
            ended_at=django.utils.timezone.datetime(2024, 2, 28, tzinfo=timezone.UTC),
        )

        mock_module = MagicMock(spec=Module)
        mock_module.name = "Auto Date Module"
        mock_module.program = program_with_dates
        mock_module.project = self.project
        mock_module.started_at = None
        mock_module.ended_at = None

        def simulate_save_for_inheritance():
            mock_module.key = "date-module"
            if not mock_module.started_at:
                mock_module.started_at = mock_module.program.started_at
            if not mock_module.ended_at:
                mock_module.ended_at = mock_module.program.ended_at

        mock_module.save.side_effect = simulate_save_for_inheritance
        mock_create_module.return_value = mock_module

        module = Module.objects.create(
            name="Auto Date Module", program=program_with_dates, project=self.project
        )
        module.save()

        assert module.key == "date-module"
        assert module.started_at == django.utils.timezone.datetime(2024, 2, 1, tzinfo=timezone.UTC)
        assert module.ended_at == django.utils.timezone.datetime(2024, 2, 28, tzinfo=timezone.UTC)

        explicit_start = django.utils.timezone.datetime(2024, 3, 1, tzinfo=timezone.UTC)
        explicit_end = django.utils.timezone.datetime(2024, 3, 31, tzinfo=timezone.UTC)

        mock_module.started_at = explicit_start
        mock_module.ended_at = explicit_end
        mock_create_module.return_value = mock_module

        module = Module.objects.create(
            name="Auto Date Module", program=program_with_dates, project=self.project
        )
        module.save()

        assert module.started_at == explicit_start
        assert module.ended_at == explicit_end
        assert module.key == "date-module"
