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

echo "Creating configuration file with custom headers..."
:> ./config.toml

echo "MAX_TIME = 300" >> ./config.toml
echo "[CUSTOM_HEADERS]" >> ./config.toml
echo "X-CSRFToken = \"$CSRF_TOKEN\"" >> ./config.toml
echo "Cookie = \"csrftoken=$CSRF_TOKEN;\"" >> ./config.toml

cat ./config.toml

echo "Running Graphqler with custom configuration..."

python -m graphqler --mode run --url "$BASE_URL/graphql/" --path ./fuzzing_results --config ./config.toml
