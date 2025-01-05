"""Geocoding utils."""

import time

from geopy.geocoders import Nominatim

from apps.common.utils import get_nest_user_agent


def get_location_coordinates(query, delay=2):
    """Get location geo coordinates."""
    time.sleep(delay)
    return Nominatim(timeout=3, user_agent=get_nest_user_agent()).geocode(query)
