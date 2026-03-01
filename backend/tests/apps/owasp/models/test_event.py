"""Tests for OWASP Event model."""

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.owasp.models import Event


@pytest.mark.django_db
class TestEventUpcomingEvents:
    """Test Event.upcoming_events() queryset and filtering logic."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data for event tests."""
        self.today = timezone.now().date()
        self.yesterday = self.today - timedelta(days=1)
        self.tomorrow = self.today + timedelta(days=1)

        # Event that started yesterday (should be excluded)
        self.past_event = Event.objects.create(
            name="Past Event",
            key="past_event",
            start_date=self.yesterday,
            url="https://example.com/past",
        )

        # Event starting today (should be INCLUDED - this is the regression test)
        self.today_event = Event.objects.create(
            name="Today Event",
            key="today_event",
            start_date=self.today,
            url="https://example.com/today",
        )

        # Event starting tomorrow (should be included)
        self.future_event = Event.objects.create(
            name="Future Event",
            key="future_event",
            start_date=self.tomorrow,
            url="https://example.com/future",
        )

        # Event with empty name (should be excluded by the exclude filter)
        self.no_name_event = Event.objects.create(
            name="",
            key="no_name_event",
            start_date=self.today,
            url="https://example.com",
        )

        # Event with empty URL (should be excluded by the exclude filter)
        self.no_url_event = Event.objects.create(
            name="No URL Event",
            key="no_url_event",
            start_date=self.today,
            url="",
        )

    def test_upcoming_events_includes_today(self):
        """Regression test: upcoming_events() must include events starting today."""
        upcoming = Event.upcoming_events()
        assert self.today_event in upcoming
        assert self.past_event not in upcoming

    def test_upcoming_events_includes_future(self):
        """Upcoming events should include future events."""
        upcoming = Event.upcoming_events()
        assert self.future_event in upcoming

    def test_upcoming_events_excludes_past(self):
        """Upcoming events should NOT include past events."""
        upcoming = Event.upcoming_events()
        assert self.past_event not in upcoming

    def test_upcoming_events_excludes_empty_name(self):
        """Upcoming events should exclude events with empty names."""
        upcoming = Event.upcoming_events()
        assert self.no_name_event not in upcoming

    def test_upcoming_events_excludes_empty_url(self):
        """Upcoming events should exclude events with empty URLs."""
        upcoming = Event.upcoming_events()
        assert self.no_url_event not in upcoming

    def test_upcoming_events_ordered_by_start_date(self):
        """Upcoming events should be ordered by start_date (ascending)."""
        upcoming = list(Event.upcoming_events())
        assert len(upcoming) == 2  # today_event and future_event
        assert upcoming[0] == self.today_event  # today comes first
        assert upcoming[1] == self.future_event  # future comes second

    def test_upcoming_events_uses_date_comparison_not_datetime(self):
        """
        Regression test: Ensure start_date__gte uses date() not raw datetime.

        This verifies the fix for the bug where DateTime comparison was silently
        excluding today's events. The query filter must compare DateField with date(),
        not with timezone.now() directly.
        """
        # Get the raw queryset to inspect the filter
        upcoming = Event.upcoming_events()
        
        # Verify today's event is in the results (not excluded by datetime comparison)
        assert self.today_event in upcoming

        # Verify the count matches expected (today + future, no past, no empty name/url)
        assert upcoming.count() == 2
