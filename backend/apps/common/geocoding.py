"""Geocoding utils."""

import time

from geopy.geocoders import Nominatim

from apps.common.utils import get_nest_user_agent


def get_location(query):
    """Get geo location."""
    time.sleep(2)
    return Nominatim(timeout=3, user_agent=get_nest_user_agent()).geocode(query)
