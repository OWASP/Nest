#!/bin/sh

set -e

if [ -z "$BASE_URL" ]; then
  echo "Error: BASE_URL environment variable is not set." >&2
  exit 1
fi

echo "Fetching CSRF token..."
CSRF_TOKEN=$(curl -fsSL "$BASE_URL/csrf" | jq -r '.csrftoken')

if [ -z "$CSRF_TOKEN" ] || [ "$CSRF_TOKEN" = "null" ]; then
  echo "Error: Failed to retrieve CSRF token." >&2
  exit 1
fi

export CSRF_TOKEN

echo "CSRF token retrieved successfully."
:> ./schemathesis.toml

# Number of examples to generate per endpoint
# See https://schemathesis.readthedocs.io/en/stable/explanations/data-generation/#how-many-test-cases-does-schemathesis-generate

echo "generation.max-examples = 100" >> ./schemathesis.toml

# Enable specific checks
# See https://schemathesis.readthedocs.io/en/stable/reference/checks/
# Schemathesis raises errors for bad requests, so we need to explicitly enable the checks we want
echo "[checks]" >> ./schemathesis.toml
echo "enabled = false" >> ./schemathesis.toml
echo "response_schema_conformance.enabled = true" >> ./schemathesis.toml

# Schemathesis raises GraphQL errors for invalid queries like invalid enums.
# We need to explicitly enable the not_a_server_error in REST API only to avoid GraphQL false positives.
if [ -n "$REST_URL" ]; then
  echo "not_a_server_error.enabled = true" >> ./schemathesis.toml
fi

if [ -n "$TEST_FILE" ]; then
    echo "Using test file: $TEST_FILE"
else
    echo "Error: TEST_FILE environment variable is not set." >&2
    exit 1
fi

echo "Starting fuzzing process..."

if [ -n "$CI" ]; then
    pytest -s ./tests/${TEST_FILE}
else
    pytest --log-cli-level=INFO -s ./tests/${TEST_FILE}
fi
