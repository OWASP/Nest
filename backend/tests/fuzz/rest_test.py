"""OWASP Nest REST API fuzz tests."""

import logging
import os

import schemathesis

if not (REST_URL := os.getenv("REST_URL")) or not (CSRF_TOKEN := os.getenv("CSRF_TOKEN")):
    message = "REST_URL and CSRF_TOKEN must be set in the environment."
    raise ValueError(message)

HEADERS = {
    "Cookie": f"csrftoken={CSRF_TOKEN}",
    "X-CSRFToken": CSRF_TOKEN,
}

logger = logging.getLogger(__name__)
schema = schemathesis.openapi.from_url(
    f"{REST_URL}/openapi.json",
    headers=HEADERS,
    timeout=30,
    wait_for_schema=10,
)


@schema.parametrize()
def test_rest_api(case):
    """Test REST API endpoints."""
    logger.info(case.as_curl_command())
    case.call_and_validate(headers=HEADERS)
