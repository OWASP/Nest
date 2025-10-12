#!/bin/sh

python manage.py migrate --run-syncdb --noinput
python manage.py collectstatic --noinput

# Load initial data
echo "Loading initial data..."
python manage.py load_data > /dev/null 2>&1
echo "Initial data loaded."

# Run fuzz tests
echo "Running fuzz tests..."
pytest fuzz_tests

# Start the Django server
python manage.py runserver 0.0.0.0:8000
