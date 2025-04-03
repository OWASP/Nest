#!/bin/bash

set -e

python manage.py migrate --database fuzz_tests
python manage.py collectstatic --noinput

pytest fuzz_tests
