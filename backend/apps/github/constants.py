"""GitHub app constants."""

import re

GITHUB_ITEMS_PER_PAGE = 100
GITHUB_ORGANIZATION_RE = re.compile("^https://github.com/([^/]+)/?$")
GITHUB_REPOSITORY_RE = re.compile("^https://github.com/([^/]+)/([^/]+)/?$")
