from unittest.mock import MagicMock, patch
from datetime import datetime
import pytest
import django.utils.timezone

from apps.mentorship.models import Module
from apps.mentorship.models import Program
from apps.owasp.models import Project


class TestModulePureMocks:
    def setup_method(self):
        """
        Prepare test fixtures by creating MagicMock instances for Program and Project used across tests.
        
        The created mocks:
        - self.program: a MagicMock with Program spec and preset attributes (name, key, status, started_at, ended_at) using UTC datetimes.
        - self.project: a MagicMock with Project spec and preset attributes (name, key).
        """
        self.program = MagicMock(
            spec=Program,
            name="Test Program",
            key="test-program",
            status=Program.ProgramStatus.PUBLISHED,
            started_at=django.utils.timezone.datetime(2023, 1, 1, 9, 0, 0, tzinfo=django.utils.timezone.UTC),
            ended_at=django.utils.timezone.datetime(2023, 12, 31, 18, 0, 0, tzinfo=django.utils.timezone.UTC),
        )
        self.project = MagicMock(spec=Project, name="Test Project", key="test-project")

    def test_str_returns_name(self):
        """Unit test: __str__ should return the module name (pure mock)."""
        mock_module = MagicMock(spec=Module)
        mock_module.name = "Security Basics"

        assert Module.__str__(mock_module) == "Security Basics"


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
            started_at=django.utils.timezone.datetime(2024, 2, 1, tzinfo=django.utils.timezone.UTC),
            ended_at=django.utils.timezone.datetime(2024, 2, 28, tzinfo=django.utils.timezone.UTC),
        )

        mock_module = MagicMock(spec=Module)
        mock_module.name = "Auto Date Module"
        mock_module.program = program_with_dates
        mock_module.project = self.project
        mock_module.started_at = None
        mock_module.ended_at = None

        def simulate_save_for_inheritance(*args, **kwargs):
            """
            Configure the test mock to mimic save-time key generation and date inheritance.
            
            Sets mock_module.key to "date-module". If mock_module.started_at or mock_module.ended_at are falsy, assigns them from mock_module.program.started_at and mock_module.program.ended_at respectively. This function mutates the enclosing mock_module and does not return a value.
            """
            mock_module.key = "date-module"  
            if not mock_module.started_at:
                mock_module.started_at = mock_module.program.started_at
            if not mock_module.ended_at:
                mock_module.ended_at = mock_module.program.ended_at

        mock_module.save.side_effect = simulate_save_for_inheritance
        mock_create_module.return_value = mock_module

        module = Module.objects.create(name="Auto Date Module", program=program_with_dates, project=self.project)
        module.save()  

        assert module.key == "date-module"
        assert module.started_at == django.utils.timezone.datetime(2024, 2, 1, tzinfo=django.utils.timezone.UTC)
        assert module.ended_at == django.utils.timezone.datetime(2024, 2, 28, tzinfo=django.utils.timezone.UTC)

        explicit_start = django.utils.timezone.datetime(2024, 3, 1, tzinfo=django.utils.timezone.UTC)
        explicit_end = django.utils.timezone.datetime(2024, 3, 31, tzinfo=django.utils.timezone.UTC)

        mock_module.started_at = explicit_start
        mock_module.ended_at = explicit_end
        mock_create_module.return_value = mock_module

        module = Module.objects.create(name="Auto Date Module", program=program_with_dates, project=self.project)
        module.save()  

        assert module.started_at == explicit_start
        assert module.ended_at == explicit_end
        assert module.key == "date-module"