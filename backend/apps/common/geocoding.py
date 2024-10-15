"""Geocoding utils."""

import logging
import time
from functools import lru_cache

import requests
from geopy.geocoders import Nominatim

from apps.common.utils import get_nest_user_agent

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1024)
def get_ip_coordinates(ip_address):
    """Return IP address geo coordinates."""
    if not ip_address:
        return None

    try:
        response = requests.get(f"https://ipapi.co/{ip_address}/latlong/", timeout=5)
        if response.status_code == requests.codes.ok:
            return response.text.split(",")
    except TypeError:
        logger.exception(
            "Could not get coordinates for the IP address",
            extra={"ip_address": ip_address},
        )
        return None


def get_location_coordinates(query, delay=2):
    """Get location geo coordinates."""
    time.sleep(delay)
    return Nominatim(timeout=3, user_agent=get_nest_user_agent()).geocode(query)
