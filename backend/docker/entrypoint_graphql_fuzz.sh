#!/bin/sh

echo "Retrieving CSRF token..."

CSRF_TOKEN=$(curl -s http://backend:8000/csrf/ | jq -r '.csrftoken')

if [ -z "$CSRF_TOKEN" ]; then
  echo "Failed to retrieve CSRF token"
  exit 1
fi

echo "CSRF token retrieved successfully: $CSRF_TOKEN"

cat > /home/owasp/config.toml << EOF
[CUSTOM_HEADERS]
X-CSRF-Token = "$CSRF_TOKEN"
EOF

echo "Custom headers configuration file created successfully"

sleep 5

echo "Starting fuzzing tests..."
python -m graphqler --config /home/owasp/config.toml --url http://backend:8000/graphql/ --mode run --path /home/owasp/fuzzing_results
