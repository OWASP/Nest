#!/bin/sh

set -e

echo "Fetching CSRF token..."
CSRF_TOKEN=$(wget -qO- "$BASE_URL/csrf" | jq -r '.csrftoken')

echo "Creating configuration file with custom headers..."
touch ./config.toml

echo "MAX_TIME = 300" >> ./config.toml
echo "[CUSTOM_HEADERS]" >> ./config.toml
echo "X-CSRFToken = \"$CSRF_TOKEN\"" >> ./config.toml
echo "Cookie = \"csrftoken=$CSRF_TOKEN;\"" >> ./config.toml

echo "Running Graphqler with custom configuration..."
uv run graphqler --mode run --url "$BASE_URL/graphql/" --path ./ --config ./config.toml
