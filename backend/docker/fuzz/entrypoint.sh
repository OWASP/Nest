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

echo "CSRF token retrieved: $CSRF_TOKEN"
:> ./schemathesis.toml

# Number of examples to generate per endpoint
# See https://schemathesis.readthedocs.io/en/stable/explanations/data-generation/#how-many-test-cases-does-schemathesis-generate

echo "generation.max-examples = 100" >> ./schemathesis.toml

echo "Starting fuzzing process..."
pytest -s ./tests/${TEST_FILE}
