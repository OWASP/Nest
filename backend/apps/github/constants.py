"""GitHub app constants."""

import re

GITHUB_ACTIONS_USER_LOGIN = "actions-user"
GITHUB_GHOST_USER_LOGIN = "ghost"
GITHUB_ITEMS_PER_PAGE = 100
GITHUB_REPOSITORY_RE = re.compile("^https://github.com/([^/]+)/([^/]+)(/.*)?$")
GITHUB_USER_RE = re.compile("^https://github.com/([^/]+)/?$")

OWASP_FOUNDATION_LOGIN = "OWASPFoundation"
OWASP_GITHUB_IO = "owasp.github.io"
OWASP_LOGIN = "owasp"
GITHUB_COMMITS_BULK_SAVE_CHUNK_SIZE = 50
