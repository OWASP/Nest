from datetime import datetime
from unittest.mock import MagicMock, patch

from apps.mentorship.models.common.start_end_range import StartEndRange


class TestStartEndRange:
    def test_fields(self):
        start_time = datetime(2023, 1, 1, 10, 0, 0)
        end_time = datetime(2023, 1, 1, 11, 0, 0)

        mock_instance = MagicMock(spec=StartEndRange)
        mock_instance.started_at = start_time
        mock_instance.ended_at = end_time
        instance = mock_instance

        assert instance.started_at == start_time
        assert instance.ended_at == end_time
