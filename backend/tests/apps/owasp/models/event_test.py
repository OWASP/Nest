from datetime import date
from unittest.mock import Mock, patch

import pytest

from apps.owasp.models.event import Event


class TestEventModel:
    @pytest.mark.parametrize(
        ("name", "key", "expected_str"),
        [
            ("event1", "", "event1"),
            ("", "key1", "key1"),
            ("", "", ""),
        ],
    )
    def test_event_str(self, name, key, expected_str):
        event = Event(name=name, key=key, start_date=date(2025, 1, 1))
        assert str(event) == expected_str

    def test_bulk_save(self):
        mock_event = [
            Mock(id=None, start_date=date(2025, 1, 1)),
            Mock(id=1, start_date=date(2025, 1, 1)),
        ]
        with patch("apps.owasp.models.event.BulkSaveModel.bulk_save") as mock_bulk_save:
            Event.bulk_save(mock_event, fields=["name"])
            mock_bulk_save.assert_called_once_with(Event, mock_event, fields=["name"])
