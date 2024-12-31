"""GitHub app constants."""

import re

GITHUB_GHOST_USER_LOGIN = "ghost"
GITHUB_ITEMS_PER_PAGE = 100
GITHUB_REPOSITORY_RE = re.compile("^https://github.com/([^/]+)/([^/]+)(/.*)?$")
GITHUB_USER_RE = re.compile("^https://github.com/([^/]+)/?$")

OWASP_FOUNDATION_LOGIN = "OWASPFoundation"
OWASP_LOGIN = "owasp"
