"""Geocoding utils."""

import time

from geopy.geocoders import Nominatim
from geopy.location import Location

from apps.common.utils import get_nest_user_agent


def get_location_coordinates(query: str, delay: int = 2) -> Location:
    """Get location geo coordinates.

    Args:
        query (str): The location query string.
        delay (int, optional): Delay in seconds before making the request.

    Returns:
        Location|None: The geopy Location object or None if not found.

    """
    time.sleep(delay)
    return Nominatim(timeout=3, user_agent=get_nest_user_agent()).geocode(query)
