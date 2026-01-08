from datetime import datetime
from unittest.mock import MagicMock

import django.utils.timezone

from apps.mentorship.models.common.start_end_range import StartEndRange


class TestStartEndRange:
    def test_fields(self):
        start_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=django.utils.timezone.UTC)
        end_time = datetime(2023, 1, 1, 11, 0, 0, tzinfo=django.utils.timezone.UTC)

        mock_instance = MagicMock(spec=StartEndRange)
        mock_instance.started_at = start_time
        mock_instance.ended_at = end_time
        instance = mock_instance

        assert instance.started_at == start_time
        assert instance.ended_at == end_time
