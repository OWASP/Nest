"""OWASP app homepage view."""

import requests
from django.http import HttpResponseRedirect
from django.views.decorators.cache import cache_page


@cache_page(60 * 68 * 24)
def home_page(_):
    """Homepage view."""
    return HttpResponseRedirect("https://owasp.org/www-project-nest", status=requests.codes.found)
