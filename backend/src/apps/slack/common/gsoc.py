"""Slack bot shared helpers for GSoC."""

import calendar

from django.utils import timezone


def get_gsoc_year():
    """Return the active GSoC program year for the current date.

    From February through December, this is the calendar year. In January it is
    the previous calendar year (the prior cycle is still treated as current until
    February).
    """
    now = timezone.now()
    return now.year if now.month >= calendar.FEBRUARY else now.year - 1
