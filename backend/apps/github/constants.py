"""GitHub app constants."""

import re

GITHUB_GHOST_USER_LOGIN = "ghost"
GITHUB_ITEMS_PER_PAGE = 100
GITHUB_REPOSITORY_RE = re.compile("^https://github.com/([^/]+)/([^/]+)(/.*)?$")
GITHUB_USER_RE = re.compile("^https://github.com/([^/]+)/?$")

OWASP_FOUNDATION_LOGIN = "OWASPFoundation"
OWASP_LOGIN = "owasp"


GITHUB_LOGIN_REQUIRED = "GitHub login is required"
GITHUB_NODE_ID_REQUIRED = "GitHub node ID is required"
GITHUB_USER_DATA_REQUIRED = "GitHub user data is required"
GITHUB_NODE_ID_NOT_FOUND = "Could not determine GitHub node ID"
