#!/bin/sh

echo "Retrieving CSRF token..."

CSRF_TOKEN=$(curl -s http://backend:8000/csrf/ | jq -r '.csrfToken')

if [ -z "$CSRF_TOKEN" ]; then
  echo "Failed to retrieve CSRF token"
  exit 1
fi

echo "CSRF token retrieved successfully"

cat > /home/owasp/config.toml << EOF
[Custom Headers]
X-CSRF-Token = "$CSRF_TOKEN"
EOF
echo "Custom headers configuration file created successfully"
echo "Starting fuzzing tests..."
python -m graphqler --config /home/owasp/config.toml --url http://backend:8000/graphql --mode run
