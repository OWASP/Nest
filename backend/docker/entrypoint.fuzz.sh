#!/bin/sh

set -e

echo "Fetching CSRF token..."
CSRF_TOKEN=$(wget -qO- http://backend:9000/csrf | jq -r '.csrftoken')

echo "Creating configuration file with custom headers..."
touch ./config.toml

echo "[CUSTOM_HEADERS]" >> ./config.toml
echo "X-CSRFToken = \"$CSRF_TOKEN\"" >> ./config.toml
echo "Cookie = \"csrftoken=$CSRF_TOKEN;\"" >> ./config.toml

echo "Running Graphqler with custom configuration..."
uv run graphqler --mode run --url http://backend:9000/graphql/ --path ./ --config ./config.toml
