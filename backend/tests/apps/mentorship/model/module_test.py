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
            started_at=django.utils.timezone.datetime(
                2023, 1, 1, 9, 0, 0, tzinfo=django.utils.timezone.UTC
            ),
            ended_at=django.utils.timezone.datetime(
                2023, 12, 31, 18, 0, 0, tzinfo=django.utils.timezone.UTC
            ),
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
            started_at=django.utils.timezone.datetime(
                2024, 2, 1, tzinfo=django.utils.timezone.UTC
            ),
            ended_at=django.utils.timezone.datetime(2024, 2, 28, tzinfo=django.utils.timezone.UTC),
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
        assert module.started_at == django.utils.timezone.datetime(
            2024, 2, 1, tzinfo=django.utils.timezone.UTC
        )
        assert module.ended_at == django.utils.timezone.datetime(
            2024, 2, 28, tzinfo=django.utils.timezone.UTC
        )

        explicit_start = django.utils.timezone.datetime(
            2024, 3, 1, tzinfo=django.utils.timezone.UTC
        )
        explicit_end = django.utils.timezone.datetime(
            2024, 3, 31, tzinfo=django.utils.timezone.UTC
        )

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

    @patch("apps.common.models.TimestampedModel.save")
    def test_save_inherits_dates_from_program(self, mock_super_save):
        """Test save method inherits dates from program when not set."""
        program_started = django.utils.timezone.datetime(
            2024, 1, 1, tzinfo=django.utils.timezone.UTC
        )
        program_ended = django.utils.timezone.datetime(
            2024, 12, 31, tzinfo=django.utils.timezone.UTC
        )

        mock_module = MagicMock(spec=Module)
        mock_module.name = "Test Module"
        mock_module.program = MagicMock(started_at=program_started, ended_at=program_ended)
        mock_module.started_at = None
        mock_module.ended_at = None

        Module.save(mock_module)

        assert mock_module.started_at == program_started
        assert mock_module.ended_at == program_ended
        mock_super_save.assert_called_once()

    @patch("apps.common.models.TimestampedModel.save")
    def test_save_keeps_explicit_dates(self, mock_super_save):
        """Test save method keeps explicitly set dates."""
        explicit_start = django.utils.timezone.datetime(
            2024, 3, 1, tzinfo=django.utils.timezone.UTC
        )
        explicit_end = django.utils.timezone.datetime(
            2024, 6, 30, tzinfo=django.utils.timezone.UTC
        )

        mock_module = MagicMock(spec=Module)
        mock_module.name = "Test Module"
        mock_module.program = MagicMock(
            started_at=django.utils.timezone.datetime(
                2024, 1, 1, tzinfo=django.utils.timezone.UTC
            ),
            ended_at=django.utils.timezone.datetime(
                2024, 12, 31, tzinfo=django.utils.timezone.UTC
            ),
        )
        mock_module.started_at = explicit_start
        mock_module.ended_at = explicit_end

        Module.save(mock_module)

        assert mock_module.started_at == explicit_start
        assert mock_module.ended_at == explicit_end

    @patch("apps.common.models.TimestampedModel.save")
    def test_save_sets_key_from_name(self, mock_super_save):
        """Test save method sets key from slug name."""
        mock_module = MagicMock(spec=Module)
        mock_module.name = "My Test Module"
        mock_module.program = MagicMock(
            started_at=django.utils.timezone.datetime(
                2024, 1, 1, tzinfo=django.utils.timezone.UTC
            ),
            ended_at=django.utils.timezone.datetime(
                2024, 12, 31, tzinfo=django.utils.timezone.UTC
            ),
        )
        mock_module.started_at = django.utils.timezone.datetime(
            2024, 1, 1, tzinfo=django.utils.timezone.UTC
        )
        mock_module.ended_at = django.utils.timezone.datetime(
            2024, 12, 31, tzinfo=django.utils.timezone.UTC
        )

        Module.save(mock_module)

        assert mock_module.key == "my-test-module"
        mock_super_save.assert_called_once()

    @patch("apps.common.models.TimestampedModel.save")
    def test_save_without_program(self, mock_super_save):
        """Test save method works when program is None."""
        mock_module = MagicMock(spec=Module)
        mock_module.name = "Orphan Module"
        mock_module.program = None
        mock_module.started_at = django.utils.timezone.datetime(
            2024, 1, 1, tzinfo=django.utils.timezone.UTC
        )
        mock_module.ended_at = django.utils.timezone.datetime(
            2024, 12, 31, tzinfo=django.utils.timezone.UTC
        )

        Module.save(mock_module)

        assert mock_module.key == "orphan-module"
        mock_super_save.assert_called_once()
