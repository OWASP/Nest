#!/bin/sh

set -e

if [ -z "$BASE_URL" ]; then
  echo "Error: BASE_URL environment variable is not set."
  exit 1
fi

echo "Fetching CSRF token..."
CSRF_TOKEN=$(curl -fsSL "$BASE_URL/csrf" | jq -r '.csrftoken')

echo "Creating configuration file with custom headers..."
:> ./config.toml

echo "MAX_TIME = 300" >> ./config.toml
echo "[CUSTOM_HEADERS]" >> ./config.toml
echo "X-CSRFToken = \"$CSRF_TOKEN\"" >> ./config.toml
echo "Cookie = \"csrftoken=$CSRF_TOKEN;\"" >> ./config.toml

cat ./config.toml

echo "Running Graphqler with custom configuration..."

python -m graphqler --mode run --url "$BASE_URL/graphql/" --path ./ --config ./config.toml
