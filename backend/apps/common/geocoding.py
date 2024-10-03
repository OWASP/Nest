"""Geocoding utils."""

import time
from functools import lru_cache

import requests
from geopy.geocoders import Nominatim

from apps.common.utils import get_nest_user_agent


@lru_cache(maxsize=1024)
def get_ip_coordinates(ip_address):
    """Return IP address geo coordinates."""
    latitude, longitude = None, None
    if ip_address:
        response = requests.get(f"https://ipapi.co/{ip_address}/latlong/", timeout=5)
        if response.status_code == requests.codes.ok:
            latitude, longitude = response.text.split(",")

    return latitude, longitude


def get_location_coordinates(query):
    """Get location geo coordinates."""
    time.sleep(2)
    return Nominatim(timeout=3, user_agent=get_nest_user_agent()).geocode(query)
